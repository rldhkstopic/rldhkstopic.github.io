import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../providers/log_provider.dart';
import '../models/daily_log.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final FocusNode _focusNode = FocusNode();
  DateTime _selectedDate = DateTime.now();
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    _messageController.addListener(() {
      setState(() {}); // 텍스트 변경 시 UI 업데이트
    });
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  Future<void> _sendMessage() async {
    final content = _messageController.text.trim();
    if (content.isEmpty) return;

    setState(() {
      _isSubmitting = true;
    });

    final success = await context.read<LogProvider>().addLog(
          content,
        );

    setState(() {
      _isSubmitting = false;
    });

    if (success) {
      _messageController.clear();
      _focusNode.unfocus();
      // 스크롤을 맨 아래로
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (_scrollController.hasClients) {
          _scrollController.animateTo(
            _scrollController.position.maxScrollExtent,
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeOut,
          );
        }
      });
    } else {
      if (mounted) {
        final error = context.read<LogProvider>().error ?? '저장에 실패했습니다';
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(error),
            backgroundColor: Colors.red[600],
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(10),
            ),
            margin: const EdgeInsets.all(16),
          ),
        );
      }
    }
  }

  void _selectDate(DateTime date) {
    setState(() {
      _selectedDate = date;
    });
    context.read<LogProvider>().loadLogsForDate(date);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      resizeToAvoidBottomInset: true,
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            // 상단: 월 표시
            _buildMonthHeader(),
            
            // 날짜 선택 바
            _buildDateSelector(),
            
            // 구분선
            Divider(height: 1, color: Colors.grey[200]),
            
            // 컨텐츠 영역
            Expanded(
              child: _buildContentArea(),
            ),
            
            // 하단: 채팅 입력창
            _buildChatInput(),
          ],
        ),
      ),
    );
  }

  Widget _buildMonthHeader() {
    final monthFormat = DateFormat('yyyy년 M월');
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 8, 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            monthFormat.format(_selectedDate),
            style: const TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.w600,
              color: Colors.black,
              letterSpacing: -0.5,
            ),
          ),
          IconButton(
            icon: Icon(Icons.refresh, size: 22, color: Colors.grey[800]),
            onPressed: () {
              context.read<LogProvider>().refresh();
            },
            padding: EdgeInsets.zero,
            constraints: const BoxConstraints(),
            tooltip: '새로고침',
          ),
        ],
      ),
    );
  }

  Widget _buildDateSelector() {
    final now = DateTime.now();
    final currentMonth = _selectedDate.month;
    final currentYear = _selectedDate.year;
    
    // 현재 월의 첫 날과 마지막 날
    final firstDay = DateTime(currentYear, currentMonth, 1);
    
    // 표시할 날짜 리스트 (현재 일부터 과거로)
    final List<DateTime> dates = [];
    final today = DateTime(now.year, now.month, now.day);
    final selectedDay = DateTime(_selectedDate.year, _selectedDate.month, _selectedDate.day);
    
    // 오늘부터 첫 날까지
    for (var date = today; date.isAfter(firstDay.subtract(const Duration(days: 1))); date = date.subtract(const Duration(days: 1))) {
      if (date.month == currentMonth && date.year == currentYear) {
        dates.add(date);
      }
    }
    
    // 첫 날부터 역순으로 정렬
    dates.sort((a, b) => b.compareTo(a));

    return Container(
      height: 56,
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 12),
        itemCount: dates.length,
        itemBuilder: (context, index) {
          final date = dates[index];
          final day = date.day;
          final isToday = date.year == now.year && 
                         date.month == now.month && 
                         date.day == now.day;
          final isSelected = date.year == selectedDay.year &&
                            date.month == selectedDay.month &&
                            date.day == selectedDay.day;
          
          return GestureDetector(
            onTap: () => _selectDate(date),
            child: Container(
              width: 44,
              margin: const EdgeInsets.symmetric(horizontal: 3),
              decoration: BoxDecoration(
                color: isSelected 
                    ? Colors.black
                    : Colors.transparent,
                borderRadius: BorderRadius.circular(22),
              ),
              child: Center(
                child: Text(
                  '$day',
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: isSelected 
                        ? FontWeight.w600 
                        : isToday
                            ? FontWeight.w500
                            : FontWeight.w400,
                    color: isSelected
                        ? Colors.white
                        : isToday
                            ? Colors.black
                            : Colors.grey[700],
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildContentArea() {
    return Consumer<LogProvider>(
      builder: (context, provider, child) {
        if (provider.isLoading && provider.logs.isEmpty) {
          return const Center(
            child: CircularProgressIndicator(
              strokeWidth: 2,
            ),
          );
        }

        if (provider.error != null && provider.logs.isEmpty) {
          final isAuthError = provider.error!.contains('401') || 
                              provider.error!.contains('Bad credentials') ||
                              provider.error!.contains('인증');
          
          return Center(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    isAuthError ? Icons.lock_outline : Icons.error_outline,
                    size: 56,
                    color: Colors.grey[400],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    isAuthError 
                        ? 'GitHub 인증 오류'
                        : '오류가 발생했습니다',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                      color: Colors.grey[800],
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    isAuthError
                        ? 'lib/config/config.dart 파일에서\nGitHub Token을 확인해주세요.'
                        : provider.error!,
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey[600],
                      height: 1.5,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: () => provider.refresh(),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.black,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 24,
                        vertical: 12,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    child: const Text('다시 시도'),
                  ),
                ],
              ),
            ),
          );
        }

        if (provider.logs.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.edit_outlined, size: 56, color: Colors.grey[300]),
                const SizedBox(height: 16),
                Text(
                  '기록이 없습니다',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                    color: Colors.grey[600],
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  '하단 입력창에 일상을 기록해보세요',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[500],
                  ),
                ),
              ],
            ),
          );
        }

        return ListView.builder(
          controller: _scrollController,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          itemCount: provider.logs.length,
          itemBuilder: (context, index) {
            final log = provider.logs[index];
            return _LogCard(log: log);
          },
        );
      },
    );
  }

  Widget _buildChatInput() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border(
          top: BorderSide(color: Colors.grey[200]!, width: 0.5),
        ),
      ),
      child: SafeArea(
        top: false,
        child: Padding(
          padding: EdgeInsets.only(
            left: 16,
            right: 16,
            top: 8,
            bottom: MediaQuery.of(context).viewInsets.bottom > 0 
                ? 8 
                : MediaQuery.of(context).padding.bottom > 0 
                    ? 0 
                    : 8,
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Expanded(
                child: Container(
                  constraints: const BoxConstraints(maxHeight: 100),
                  decoration: BoxDecoration(
                    color: Colors.grey[100],
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: TextField(
                    controller: _messageController,
                    focusNode: _focusNode,
                    decoration: const InputDecoration(
                      hintText: '일상을 기록하세요...',
                      hintStyle: TextStyle(
                        color: Colors.grey,
                        fontSize: 15,
                      ),
                      border: InputBorder.none,
                      contentPadding: EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 10,
                      ),
                    ),
                    style: const TextStyle(
                      fontSize: 15,
                      color: Colors.black87,
                    ),
                    maxLines: null,
                    textInputAction: TextInputAction.send,
                    onSubmitted: (_) => _sendMessage(),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: _messageController.text.trim().isNotEmpty || _isSubmitting
                      ? Colors.black
                      : Colors.grey[300],
                  shape: BoxShape.circle,
                ),
                child: Material(
                  color: Colors.transparent,
                  child: InkWell(
                    borderRadius: BorderRadius.circular(20),
                    onTap: _isSubmitting ? null : _sendMessage,
                    child: Center(
                      child: _isSubmitting
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                              ),
                            )
                          : Icon(
                              Icons.send_rounded,
                              size: 20,
                              color: _messageController.text.trim().isNotEmpty
                                  ? Colors.white
                                  : Colors.grey[600],
                            ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _LogCard extends StatelessWidget {
  final DailyLog log;

  const _LogCard({required this.log});

  @override
  Widget build(BuildContext context) {
    final timeFormat = DateFormat('HH:mm');
    final dateFormat = DateFormat('yyyy-MM-dd');
    final isToday = dateFormat.format(log.timestamp) ==
        dateFormat.format(DateTime.now());

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 컨텐츠 카드
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: Colors.grey[200]!,
                width: 0.5,
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  log.content,
                  style: const TextStyle(
                    fontSize: 15,
                    height: 1.5,
                    color: Colors.black87,
                    letterSpacing: -0.2,
                  ),
                ),
                if (log.mood != null || log.location != null || log.tags != null) ...[
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 6,
                    runSpacing: 6,
                    children: [
                      if (log.mood != null)
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 5,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.grey[100],
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            log.mood!,
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey[700],
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                      if (log.location != null)
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 5,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.grey[100],
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            log.location!,
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey[700],
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                      if (log.tags != null)
                        ...log.tags!.map((tag) => Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 10,
                                vertical: 5,
                              ),
                              decoration: BoxDecoration(
                                color: Colors.grey[100],
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Text(
                                '#$tag',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey[700],
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            )),
                    ],
                  ),
                ],
              ],
            ),
          ),
          // 시간과 삭제 버튼
          Padding(
            padding: const EdgeInsets.only(top: 6, left: 4),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  timeFormat.format(log.timestamp),
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[500],
                    fontWeight: FontWeight.w400,
                  ),
                ),
                GestureDetector(
                  onTap: () async {
                    final confirmed = await showDialog<bool>(
                      context: context,
                      builder: (context) => AlertDialog(
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        title: const Text(
                          '기록 삭제',
                          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
                        ),
                        content: const Text('이 기록을 삭제하시겠습니까?'),
                        actions: [
                          TextButton(
                            onPressed: () => Navigator.pop(context, false),
                            child: Text(
                              '취소',
                              style: TextStyle(color: Colors.grey[700]),
                            ),
                          ),
                          TextButton(
                            onPressed: () => Navigator.pop(context, true),
                            child: const Text(
                              '삭제',
                              style: TextStyle(color: Colors.red),
                            ),
                          ),
                        ],
                      ),
                    );

                    if (confirmed == true && context.mounted) {
                      await context.read<LogProvider>().deleteLog(log);
                      if (context.mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: const Text('기록이 삭제되었습니다'),
                            behavior: SnackBarBehavior.floating,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10),
                            ),
                            margin: const EdgeInsets.all(16),
                          ),
                        );
                      }
                    }
                  },
                  child: Padding(
                    padding: const EdgeInsets.all(4),
                    child: Icon(
                      Icons.more_horiz,
                      size: 18,
                      color: Colors.grey[400],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
