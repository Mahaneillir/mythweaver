import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Base API client for making HTTP requests to Mythweaver backend
class ApiClient {
  // TODO: Update this to your actual backend URL
  // For local development on iOS simulator: http://localhost:8000
  // For local development on Android emulator: http://10.0.2.2:8000
  // For web: http://localhost:8000
  static const String baseUrl = 'http://localhost:8000';

  final http.Client _httpClient;
  final FlutterSecureStorage _secureStorage;

  ApiClient({http.Client? httpClient, FlutterSecureStorage? secureStorage})
    : _httpClient = httpClient ?? http.Client(),
      _secureStorage = secureStorage ?? const FlutterSecureStorage();

  /// Get stored authentication token
  Future<String?> getToken() async {
    return await _secureStorage.read(key: 'auth_token');
  }

  /// Save authentication token
  Future<void> saveToken(String token) async {
    await _secureStorage.write(key: 'auth_token', value: token);
  }

  /// Delete authentication token (logout)
  Future<void> deleteToken() async {
    await _secureStorage.delete(key: 'auth_token');
  }

  /// Make GET request
  Future<http.Response> get(
    String endpoint, {
    Map<String, String>? headers,
    bool requiresAuth = false,
  }) async {
    final url = Uri.parse('$baseUrl$endpoint');
    final requestHeaders = await _buildHeaders(headers, requiresAuth);

    return await _httpClient.get(url, headers: requestHeaders);
  }

  /// Make POST request
  Future<http.Response> post(
    String endpoint, {
    Map<String, dynamic>? body,
    Map<String, String>? headers,
    bool requiresAuth = false,
  }) async {
    final url = Uri.parse('$baseUrl$endpoint');
    final requestHeaders = await _buildHeaders(headers, requiresAuth);

    return await _httpClient.post(
      url,
      headers: requestHeaders,
      body: body != null ? jsonEncode(body) : null,
    );
  }

  /// Make PUT request
  Future<http.Response> put(
    String endpoint, {
    Map<String, dynamic>? body,
    Map<String, String>? headers,
    bool requiresAuth = false,
  }) async {
    final url = Uri.parse('$baseUrl$endpoint');
    final requestHeaders = await _buildHeaders(headers, requiresAuth);

    return await _httpClient.put(
      url,
      headers: requestHeaders,
      body: body != null ? jsonEncode(body) : null,
    );
  }

  /// Make DELETE request
  Future<http.Response> delete(
    String endpoint, {
    Map<String, String>? headers,
    bool requiresAuth = false,
  }) async {
    final url = Uri.parse('$baseUrl$endpoint');
    final requestHeaders = await _buildHeaders(headers, requiresAuth);

    return await _httpClient.delete(url, headers: requestHeaders);
  }

  /// Build request headers with auth token if needed
  Future<Map<String, String>> _buildHeaders(
    Map<String, String>? customHeaders,
    bool requiresAuth,
  ) async {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    // Add custom headers
    if (customHeaders != null) {
      headers.addAll(customHeaders);
    }

    // Add authorization header if required
    if (requiresAuth) {
      final token = await getToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }
    }

    return headers;
  }

  /// Dispose of resources
  void dispose() {
    _httpClient.close();
  }
}
