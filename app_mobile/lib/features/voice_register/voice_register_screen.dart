import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import 'package:mom_voice_chatbot/features/chat/chat_screen.dart';
import 'package:mom_voice_chatbot/core/api_client.dart';

class VoiceRegisterScreen extends ConsumerStatefulWidget {
  const VoiceRegisterScreen({super.key});

  @override
  ConsumerState<VoiceRegisterScreen> createState() => _VoiceRegisterScreenState();
}

class _VoiceRegisterScreenState extends ConsumerState<VoiceRegisterScreen> {
  String? _selectedFilePath;
  bool _isUploading = false;
  String _statusMessage = "";

  Future<void> _pickFile() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.audio,
    );

    if (result != null) {
      setState(() {
        _selectedFilePath = result.files.single.path;
      });
    }
  }

  Future<void> _uploadAndProcess() async {
    if (_selectedFilePath == null) return;
    setState(() {
      _isUploading = true;
      _statusMessage = "업로드 중...";
    });

    try {
      final client = ref.read(apiClientProvider);
      final id = await client.uploadAudio(_selectedFilePath!);
      
      setState(() {
        _statusMessage = "업로드 성공! ID: $id\\n화자 분리 중...";
      });
      
      // Navigate to chat
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => const ChatScreen()),
      );
    } catch (e) {
      setState(() {
        _statusMessage = "오류 발생: $e";
      });
    } finally {
      setState(() {
        _isUploading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("음성 등록")),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text(
                "엄마의 목소리가 담긴 오디오 파일을 업로드하세요.",
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 18),
              ),
              const SizedBox(height: 30),
              ElevatedButton.icon(
                icon: const Icon(Icons.audiotrack),
                label: const Text("파일 선택"),
                onPressed: _pickFile,
              ),
              const SizedBox(height: 20),
              if (_selectedFilePath != null)
                Text("선택됨: ${_selectedFilePath!.split('/').last}"),
              const SizedBox(height: 30),
              if (_isUploading)
                const CircularProgressIndicator()
              else if (_selectedFilePath != null)
                ElevatedButton(
                  onPressed: _uploadAndProcess,
                  child: const Text("화자 분리 및 학습 시작"),
                ),
              const SizedBox(height: 20),
              Text(_statusMessage, style: const TextStyle(color: Colors.red)),
            ],
          ),
        ),
      ),
    );
  }
}
