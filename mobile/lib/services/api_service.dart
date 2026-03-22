import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/activity.dart';
import '../models/sleep_record.dart';
import '../models/calendar_event.dart';
import '../models/chat_message.dart';

class ApiService {
  final String baseUrl;

  ApiService({this.baseUrl = 'http://localhost:8000'});

  // --- Health ---

  Future<bool> isReachable() async {
    try {
      final res = await http
          .get(Uri.parse('$baseUrl/health'))
          .timeout(const Duration(seconds: 3));
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  // --- Garmin ---

  Future<Map<String, dynamic>> syncGarmin() async {
    final res = await http.post(Uri.parse('$baseUrl/garmin/sync'));
    _assertOk(res);
    return jsonDecode(res.body);
  }

  Future<List<Activity>> getActivities({int days = 7}) async {
    final res = await http.get(
      Uri.parse('$baseUrl/garmin/activities?days=$days'),
    );
    _assertOk(res);
    final List<dynamic> data = jsonDecode(res.body);
    return data.map((j) => Activity.fromJson(j)).toList();
  }

  Future<List<SleepRecord>> getSleep({int days = 7}) async {
    final res = await http.get(
      Uri.parse('$baseUrl/garmin/sleep?days=$days'),
    );
    _assertOk(res);
    final List<dynamic> data = jsonDecode(res.body);
    return data.map((j) => SleepRecord.fromJson(j)).toList();
  }

  // --- Calendar ---

  Future<Map<String, dynamic>> syncCalendar() async {
    final res = await http.post(Uri.parse('$baseUrl/calendar/sync'));
    _assertOk(res);
    return jsonDecode(res.body);
  }

  Future<List<CalendarEvent>> getEvents({int days = 14}) async {
    final res = await http.get(
      Uri.parse('$baseUrl/calendar/events?days=$days'),
    );
    _assertOk(res);
    final List<dynamic> data = jsonDecode(res.body);
    return data.map((j) => CalendarEvent.fromJson(j)).toList();
  }

  // --- Coach ---

  Future<String> sendMessage(String message) async {
    final res = await http.post(
      Uri.parse('$baseUrl/coach/chat'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'message': message, 'stream': false}),
    );
    _assertOk(res);
    final data = jsonDecode(res.body);
    return data['reply'] as String;
  }

  Future<List<ChatMessage>> getChatHistory({int limit = 50}) async {
    final res = await http.get(
      Uri.parse('$baseUrl/coach/history?limit=$limit'),
    );
    _assertOk(res);
    final List<dynamic> data = jsonDecode(res.body);
    return data.map((j) => ChatMessage.fromJson(j)).toList();
  }

  Future<void> clearChatHistory() async {
    final res = await http.delete(Uri.parse('$baseUrl/coach/history'));
    _assertOk(res);
  }

  void _assertOk(http.Response res) {
    if (res.statusCode < 200 || res.statusCode >= 300) {
      String detail = '';
      try {
        detail = jsonDecode(res.body)['detail'] ?? res.body;
      } catch (_) {
        detail = res.body;
      }
      throw ApiException(res.statusCode, detail);
    }
  }
}

class ApiException implements Exception {
  final int statusCode;
  final String message;
  ApiException(this.statusCode, this.message);

  @override
  String toString() => 'ApiException($statusCode): $message';
}
