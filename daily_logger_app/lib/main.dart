import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/home_screen.dart';
import 'screens/add_log_screen.dart';
import 'providers/log_provider.dart';
import 'services/github_service.dart';
import 'config/config.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    // GitHub Service 초기화
    final githubService = GitHubService(
      token: Config.githubToken,
      repo: Config.githubRepo,
      logsDir: Config.logsDir,
    );

    return ChangeNotifierProvider(
      create: (_) => LogProvider(githubService: githubService),
      child: MaterialApp(
        title: '일상 기록',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
          useMaterial3: true,
        ),
        home: const HomeScreen(),
        routes: {
          '/add': (context) => const AddLogScreen(),
        },
      ),
    );
  }
}

