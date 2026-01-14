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

  /// 오늘의 기록 목록 로드
  Future<void> _loadTodayLogs() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _logs = await _githubService.getTodayLogs();
      _error = null;
    } catch (e) {
      _error = '기록을 불러오는데 실패했습니다: $e';
      print('[ERROR] $_error');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// 새 기록 추가
  Future<bool> addLog(String content, {String? mood, List<String>? tags, String? location}) async {
    final log = DailyLog(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: content,
      timestamp: DateTime.now(),
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
        _logs.add(log);
        _logs.sort((a, b) => a.timestamp.compareTo(b.timestamp));
        _error = null;
        notifyListeners();
        return true;
      } else {
        _error = '기록 저장에 실패했습니다.';
        notifyListeners();
        return false;
      }
    } catch (e) {
      _error = '기록 저장 중 오류가 발생했습니다: $e';
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

