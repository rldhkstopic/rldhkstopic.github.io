import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/log_provider.dart';

class AddLogScreen extends StatefulWidget {
  const AddLogScreen({super.key});

  @override
  State<AddLogScreen> createState() => _AddLogScreenState();
}

class _AddLogScreenState extends State<AddLogScreen> {
  final _contentController = TextEditingController();
  final _moodController = TextEditingController();
  final _locationController = TextEditingController();
  final _tagController = TextEditingController();
  bool _isSubmitting = false;

  @override
  void dispose() {
    _contentController.dispose();
    _moodController.dispose();
    _locationController.dispose();
    _tagController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (_contentController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('내용을 입력해주세요')),
      );
      return;
    }

    setState(() {
      _isSubmitting = true;
    });

    final tags = _tagController.text
        .split(',')
        .map((t) => t.trim())
        .where((t) => t.isNotEmpty)
        .toList();

    final success = await context.read<LogProvider>().addLog(
          _contentController.text.trim(),
          mood: _moodController.text.trim().isEmpty
              ? null
              : _moodController.text.trim(),
          location: _locationController.text.trim().isEmpty
              ? null
              : _locationController.text.trim(),
          tags: tags.isEmpty ? null : tags,
        );

    setState(() {
      _isSubmitting = false;
    });

    if (success) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('기록이 저장되었습니다'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pop(context);
      }
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(context.read<LogProvider>().error ?? '저장에 실패했습니다'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('새 기록 추가'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _contentController,
              decoration: const InputDecoration(
                labelText: '내용 *',
                hintText: '오늘 일어난 일을 기록하세요',
                border: OutlineInputBorder(),
              ),
              maxLines: 8,
              autofocus: true,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _moodController,
              decoration: const InputDecoration(
                labelText: '기분 (선택)',
                hintText: '예: 기쁨, 슬픔, 평온 등',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _locationController,
              decoration: const InputDecoration(
                labelText: '위치 (선택)',
                hintText: '예: 집, 회사, 카페 등',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _tagController,
              decoration: const InputDecoration(
                labelText: '태그 (선택)',
                hintText: '쉼표로 구분하여 입력 (예: 작업, 운동, 독서)',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: _isSubmitting ? null : _submit,
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: _isSubmitting
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('저장하기'),
            ),
          ],
        ),
      ),
    );
  }
}

