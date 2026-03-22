class CalendarEvent {
  final int id;
  final String googleId;
  final String summary;
  final String? description;
  final DateTime startTime;
  final DateTime? endTime;
  final bool isAllDay;
  final String? calendarName;

  CalendarEvent({
    required this.id,
    required this.googleId,
    required this.summary,
    this.description,
    required this.startTime,
    this.endTime,
    required this.isAllDay,
    this.calendarName,
  });

  factory CalendarEvent.fromJson(Map<String, dynamic> json) {
    return CalendarEvent(
      id: json['id'] ?? 0,
      googleId: json['google_id'] ?? '',
      summary: json['summary'] ?? '(No title)',
      description: json['description'],
      startTime: DateTime.parse(json['start_time']),
      endTime: json['end_time'] != null ? DateTime.parse(json['end_time']) : null,
      isAllDay: json['is_all_day'] ?? false,
      calendarName: json['calendar_name'],
    );
  }
}
