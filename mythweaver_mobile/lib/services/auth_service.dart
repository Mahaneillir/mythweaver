import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/user.dart';
import 'api_client.dart';

/// Authentication service for user signup, login, and token management
class AuthService {
  final ApiClient _apiClient;

  AuthService({ApiClient? apiClient}) : _apiClient = apiClient ?? ApiClient();

  /// Register a new user account
  /// Returns AuthResponse with access token on success
  /// Throws exception on failure
  Future<AuthResponse> register({
    required String username,
    required String email,
    required String password,
  }) async {
    try {
      final response = await _apiClient.post(
        '/auth/register',
        body: {'username': username, 'email': email, 'password': password},
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        final authResponse = AuthResponse.fromJson(data);

        // Save token automatically after successful registration
        await _apiClient.saveToken(authResponse.accessToken);

        return authResponse;
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['detail'] ?? 'Registration failed');
      }
    } catch (e) {
      throw Exception('Registration error: $e');
    }
  }

  /// Login with existing credentials
  /// Returns AuthResponse with access token on success
  /// Throws exception on failure
  Future<AuthResponse> login({
    required String username,
    required String password,
  }) async {
    try {
      final response = await _apiClient.post(
        '/auth/login',
        body: {'username': username, 'password': password},
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        final authResponse = AuthResponse.fromJson(data);

        // Save token automatically after successful login
        await _apiClient.saveToken(authResponse.accessToken);

        return authResponse;
      } else if (response.statusCode == 401) {
        throw Exception('Invalid username or password');
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['detail'] ?? 'Login failed');
      }
    } catch (e) {
      throw Exception('Login error: $e');
    }
  }

  /// Logout user and clear stored token
  Future<void> logout() async {
    await _apiClient.deleteToken();
  }

  /// Check if user is currently authenticated (has token)
  Future<bool> isAuthenticated() async {
    final token = await _apiClient.getToken();
    return token != null && token.isNotEmpty;
  }

  /// Get current auth token
  Future<String?> getToken() async {
    return await _apiClient.getToken();
  }

  /// Dispose of resources
  void dispose() {
    _apiClient.dispose();
  }
}
