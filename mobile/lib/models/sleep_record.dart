class SleepRecord {
  final int id;
  final String date;
  final double? durationSeconds;
  final int? sleepScore;
  final double? hrvNightly;
  final double? deepSleepSeconds;
  final double? remSleepSeconds;

  SleepRecord({
    required this.id,
    required this.date,
    this.durationSeconds,
    this.sleepScore,
    this.hrvNightly,
    this.deepSleepSeconds,
    this.remSleepSeconds,
  });

  factory SleepRecord.fromJson(Map<String, dynamic> json) {
    return SleepRecord(
      id: json['id'] ?? 0,
      date: json['date'] ?? '',
      durationSeconds: json['duration_seconds']?.toDouble(),
      sleepScore: json['sleep_score'],
      hrvNightly: json['hrv_nightly']?.toDouble(),
      deepSleepSeconds: json['deep_sleep_seconds']?.toDouble(),
      remSleepSeconds: json['rem_sleep_seconds']?.toDouble(),
    );
  }

  String get durationFormatted {
    if (durationSeconds == null) return '--';
    final hours = durationSeconds! ~/ 3600;
    final minutes = (durationSeconds! % 3600) ~/ 60;
    return '${hours}h ${minutes}m';
  }
}
