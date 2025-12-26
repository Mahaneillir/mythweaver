/// User model representing an authenticated user in Mythweaver
class User {
  final String id;
  final String username;
  final String email;

  User({required this.id, required this.username, required this.email});

  /// Create User from JSON response
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      username: json['username'] as String,
      email: json['email'] as String,
    );
  }

  /// Convert User to JSON
  Map<String, dynamic> toJson() {
    return {'id': id, 'username': username, 'email': email};
  }

  @override
  String toString() => 'User(id: $id, username: $username, email: $email)';
}

/// Authentication response containing access token
class AuthResponse {
  final String accessToken;
  final String tokenType;

  AuthResponse({required this.accessToken, required this.tokenType});

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      accessToken: json['accessToken'] as String,
      tokenType: json['tokenType'] as String? ?? 'bearer',
    );
  }

  Map<String, dynamic> toJson() {
    return {'accessToken': accessToken, 'tokenType': tokenType};
  }
}
