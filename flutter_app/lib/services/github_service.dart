import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:intl/intl.dart';
import '../models/daily_log.dart';
import '../config/config.dart';

class GitHubService {
  final String _baseUrl = 'https://api.github.com';
  final String _token;
  final String _repo;
  final String _logsDir;

  GitHubService({
    required String token,
    required String repo,
    required String logsDir,
  })  : _token = token,
        _repo = repo,
        _logsDir = logsDir;

  /// 일상 기록을 GitHub에 저장
  Future<bool> saveLog(DailyLog log) async {
    try {
      // 날짜별 디렉토리 경로
      final dateStr = DateFormat('yyyy-MM-dd').format(log.timestamp);
      final filename = '${log.id}.json';
      final path = '$_logsDir/$dateStr/$filename';

      // JSON 변환
      final content = jsonEncode(log.toJson());
      final contentBase64 = base64Encode(utf8.encode(content));

      // GitHub API: 파일 생성
      final url = '$_baseUrl/repos/$_repo/contents/$path';
      final response = await http.put(
        Uri.parse(url),
        headers: {
          'Authorization': 'token $_token',
          'Accept': 'application/vnd.github.v3+json',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'message': 'Add daily log: ${log.id}',
          'content': contentBase64,
        }),
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        return true;
      } else {
        print('[ERROR] GitHub API 오류: ${response.statusCode}');
        print('[ERROR] 응답: ${response.body}');
        return false;
      }
    } catch (e) {
      print('[ERROR] 기록 저장 실패: $e');
      return false;
    }
  }

  /// 특정 날짜의 기록 목록 조회
  Future<List<DailyLog>> getLogsForDate(DateTime date) async {
    try {
      final dateStr = DateFormat('yyyy-MM-dd').format(date);
      final path = '$_logsDir/$dateStr';

      // GitHub API: 디렉토리 내용 조회
      final url = '$_baseUrl/repos/$_repo/contents/$path';
      final response = await http.get(
        Uri.parse(url),
        headers: {
          'Authorization': 'token $_token',
          'Accept': 'application/vnd.github.v3+json',
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> files = jsonDecode(response.body);
        final List<DailyLog> logs = [];

        for (var file in files) {
          if (file['type'] == 'file' && file['name'].endsWith('.json')) {
            // 파일 내용 다운로드
            final fileUrl = file['download_url'];
            final fileResponse = await http.get(Uri.parse(fileUrl));

            if (fileResponse.statusCode == 200) {
              final logJson = jsonDecode(fileResponse.body);
              logs.add(DailyLog.fromJson(logJson));
            }
          }
        }

        // 타임스탬프 기준 정렬
        logs.sort((a, b) => a.timestamp.compareTo(b.timestamp));
        return logs;
      } else if (response.statusCode == 404) {
        // 디렉토리가 없으면 빈 리스트 반환
        return [];
      } else {
        print('[ERROR] 기록 조회 실패: ${response.statusCode}');
        return [];
      }
    } catch (e) {
      print('[ERROR] 기록 조회 오류: $e');
      return [];
    }
  }

  /// 당일 기록 목록 조회
  Future<List<DailyLog>> getTodayLogs() async {
    return getLogsForDate(DateTime.now());
  }

  /// 기록 삭제
  Future<bool> deleteLog(DailyLog log) async {
    try {
      final dateStr = DateFormat('yyyy-MM-dd').format(log.timestamp);
      final filename = '${log.id}.json';
      final path = '$_logsDir/$dateStr/$filename';

      // 먼저 파일 정보 조회 (SHA 필요)
      final getUrl = '$_baseUrl/repos/$_repo/contents/$path';
      final getResponse = await http.get(
        Uri.parse(getUrl),
        headers: {
          'Authorization': 'token $_token',
          'Accept': 'application/vnd.github.v3+json',
        },
      );

      if (getResponse.statusCode != 200) {
        return false;
      }

      final fileInfo = jsonDecode(getResponse.body);
      final sha = fileInfo['sha'];

      // 파일 삭제
      final deleteUrl = '$_baseUrl/repos/$_repo/contents/$path';
      final deleteResponse = await http.delete(
        Uri.parse(deleteUrl),
        headers: {
          'Authorization': 'token $_token',
          'Accept': 'application/vnd.github.v3+json',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'message': 'Delete daily log: ${log.id}',
          'sha': sha,
        }),
      );

      return deleteResponse.statusCode == 200;
    } catch (e) {
      print('[ERROR] 기록 삭제 실패: $e');
      return false;
    }
  }
}

