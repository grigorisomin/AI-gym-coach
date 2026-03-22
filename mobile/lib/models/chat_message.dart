class ChatMessage {
  final int? id;
  final String role;
  final String content;
  final DateTime createdAt;

  ChatMessage({
    this.id,
    required this.role,
    required this.content,
    required this.createdAt,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'],
      role: json['role'] ?? 'user',
      content: json['content'] ?? '',
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  bool get isUser => role == 'user';
}
