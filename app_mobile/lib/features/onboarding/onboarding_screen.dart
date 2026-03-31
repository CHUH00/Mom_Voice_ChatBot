import 'package:flutter/material.dart';
import 'package:mom_voice_chatbot/features/voice_register/voice_register_screen.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  bool _agreed = false;

  void _proceed() {
    if (_agreed) {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (context) => const VoiceRegisterScreen()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("환영합니다")),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "Mom Voice ChatBot",
              style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            const Text(
              "본 앱은 실제 인물 그 자체가 아니라 음성 및 표현 기반 보조 재현 시스템입니다.\\n"
              "명시적인 동의가 있어야만 엄마의 음성 복제 및 분석 기능이 활성화됩니다.",
              style: TextStyle(fontSize: 16, height: 1.5),
            ),
            const Spacer(),
            CheckboxListTile(
              title: const Text("위 내용을 확인하고 모델 학습 및 사용에 동의합니다."),
              value: _agreed,
              onChanged: (val) {
                setState(() => _agreed = val ?? false);
              },
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: _agreed ? _proceed : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: _agreed ? Colors.orange : Colors.grey,
                ),
                child: const Text("시작하기", style: TextStyle(color: Colors.white, fontSize: 18)),
              ),
            )
          ],
        ),
      ),
    );
  }
}
