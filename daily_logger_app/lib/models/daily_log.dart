import 'package:json_annotation/json_annotation.dart';

part 'daily_log.g.dart';

@JsonSerializable()
class DailyLog {
  final String id;
  final String content;
  final DateTime timestamp;
  final String? mood; // 기분 (선택)
  final List<String>? tags; // 태그 (선택)
  final String? location; // 위치 (선택)

  DailyLog({
    required this.id,
    required this.content,
    required this.timestamp,
    this.mood,
    this.tags,
    this.location,
  });

  factory DailyLog.fromJson(Map<String, dynamic> json) =>
      _$DailyLogFromJson(json);

  Map<String, dynamic> toJson() => _$DailyLogToJson(this);

  DailyLog copyWith({
    String? id,
    String? content,
    DateTime? timestamp,
    String? mood,
    List<String>? tags,
    String? location,
  }) {
    return DailyLog(
      id: id ?? this.id,
      content: content ?? this.content,
      timestamp: timestamp ?? this.timestamp,
      mood: mood ?? this.mood,
      tags: tags ?? this.tags,
      location: location ?? this.location,
    );
  }
}

