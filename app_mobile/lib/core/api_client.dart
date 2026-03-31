import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final dioProvider = Provider<Dio>((ref) {
  final dio = Dio(BaseOptions(
    baseUrl: 'http://localhost:8000/api', // Emulators use 10.0.2.2 usually, localhost on macOS
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 30),
  ));
  return dio;
});

class ApiClient {
  final Dio dio;

  ApiClient(this.dio);

  Future<bool> setupPin(String pin) async {
    try {
      final response = await dio.post('/auth/pin/setup', queryParameters: {'pin': pin});
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  Future<String> uploadAudio(String filePath) async {
    try {
      FormData formData = FormData.fromMap({
        "file": await MultipartFile.fromFile(filePath, filename: filePath.split('/').last),
      });
      var response = await dio.post('/audio/upload', data: formData);
      return response.data['id'].toString();
    } catch (e) {
      throw Exception('Upload failed: $e');
    }
  }

  Future<String> chatWithMom(String query) async {
    try {
      final response = await dio.post('/chat/text', queryParameters: {'message': query});
      return response.data['reply'];
    } catch (e) {
      return "엄마: (답장을 받을 수 없습니다)";
    }
  }
}

final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient(ref.watch(dioProvider));
});
