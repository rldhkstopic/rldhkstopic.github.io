// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'daily_log.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

DailyLog _$DailyLogFromJson(Map<String, dynamic> json) => DailyLog(
      id: json['id'] as String,
      content: json['content'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      mood: json['mood'] as String?,
      tags: (json['tags'] as List<dynamic>?)?.map((e) => e as String).toList(),
      location: json['location'] as String?,
    );

Map<String, dynamic> _$DailyLogToJson(DailyLog instance) => <String, dynamic>{
      'id': instance.id,
      'content': instance.content,
      'timestamp': instance.timestamp.toIso8601String(),
      'mood': instance.mood,
      'tags': instance.tags,
      'location': instance.location,
    };
