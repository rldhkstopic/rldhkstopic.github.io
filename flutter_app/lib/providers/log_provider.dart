import 'package:flutter/foundation.dart';
import '../models/daily_log.dart';
import '../services/github_service.dart';

class LogProvider with ChangeNotifier {
  final GitHubService _githubService;
  List<DailyLog> _logs = [];
  bool _isLoading = false;
  String? _error;

  LogProvider({required GitHubService githubService})
      : _githubService = githubService {
    _loadTodayLogs();
  }

  List<DailyLog> get logs => _logs;
  bool get isLoading => _isLoading;
  String? get error => _error;
  DateTime? _currentDate;

  /// 특정 날짜의 기록 목록 로드
  Future<void> loadLogsForDate(DateTime date) async {
    _currentDate = date;
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _logs = await _githubService.getLogsForDate(date);
      _error = null;
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
      print('[ERROR] $_error');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// 오늘의 기록 목록 로드
  Future<void> _loadTodayLogs() async {
    await loadLogsForDate(DateTime.now());
  }

  /// 새 기록 추가
  Future<bool> addLog(String content, {String? mood, List<String>? tags, String? location}) async {
    final now = DateTime.now();
    final log = DailyLog(
      id: now.millisecondsSinceEpoch.toString(),
      content: content,
      timestamp: now,
      mood: mood,
      tags: tags,
      location: location,
    );

    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final success = await _githubService.saveLog(log);
      if (success) {
        // 오늘 날짜의 기록이면 목록에 추가
        final today = DateTime(now.year, now.month, now.day);
        final currentDate = _currentDate != null
            ? DateTime(_currentDate!.year, _currentDate!.month, _currentDate!.day)
            : null;
        
        if (currentDate == null || currentDate == today) {
          _logs.add(log);
          _logs.sort((a, b) => a.timestamp.compareTo(b.timestamp));
        }
        _error = null;
        notifyListeners();
        return true;
      } else {
        _error = '기록 저장에 실패했습니다.';
        notifyListeners();
        return false;
      }
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// 기록 삭제
  Future<bool> deleteLog(DailyLog log) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final success = await _githubService.deleteLog(log);
      if (success) {
        _logs.remove(log);
        _error = null;
        notifyListeners();
        return true;
      } else {
        _error = '기록 삭제에 실패했습니다.';
        notifyListeners();
        return false;
      }
    } catch (e) {
      _error = '기록 삭제 중 오류가 발생했습니다: $e';
      notifyListeners();
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// 기록 목록 새로고침
  Future<void> refresh() async {
    await _loadTodayLogs();
  }
}

