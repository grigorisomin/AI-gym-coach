class Activity {
  final int id;
  final String garminId;
  final String name;
  final String activityType;
  final DateTime startTime;
  final double durationSeconds;
  final double? distanceMeters;
  final int? avgHr;
  final int? maxHr;
  final int? calories;
  final double? trainingLoad;
  final double? aerobicTrainingEffect;

  Activity({
    required this.id,
    required this.garminId,
    required this.name,
    required this.activityType,
    required this.startTime,
    required this.durationSeconds,
    this.distanceMeters,
    this.avgHr,
    this.maxHr,
    this.calories,
    this.trainingLoad,
    this.aerobicTrainingEffect,
  });

  factory Activity.fromJson(Map<String, dynamic> json) {
    return Activity(
      id: json['id'] ?? 0,
      garminId: json['garmin_id'] ?? '',
      name: json['name'] ?? 'Unknown',
      activityType: json['activity_type'] ?? 'unknown',
      startTime: DateTime.parse(json['start_time']),
      durationSeconds: (json['duration_seconds'] ?? 0).toDouble(),
      distanceMeters: json['distance_meters']?.toDouble(),
      avgHr: json['avg_hr'],
      maxHr: json['max_hr'],
      calories: json['calories'],
      trainingLoad: json['training_load']?.toDouble(),
      aerobicTrainingEffect: json['aerobic_training_effect']?.toDouble(),
    );
  }

  String get durationFormatted {
    final minutes = durationSeconds ~/ 60;
    if (minutes >= 60) {
      return '${minutes ~/ 60}h ${minutes % 60}m';
    }
    return '${minutes}m';
  }

  String get distanceFormatted {
    if (distanceMeters == null) return '';
    final km = distanceMeters! / 1000;
    return '${km.toStringAsFixed(1)} km';
  }

  String get activityEmoji {
    switch (activityType.toLowerCase()) {
      case 'running':
      case 'trail_running':
        return '🏃';
      case 'cycling':
      case 'road_biking':
      case 'mountain_biking':
        return '🚴';
      case 'swimming':
        return '🏊';
      case 'strength_training':
      case 'weightlifting':
        return '🏋️';
      case 'yoga':
        return '🧘';
      case 'hiking':
        return '🥾';
      case 'walking':
        return '🚶';
      default:
        return '⚡';
    }
  }
}
