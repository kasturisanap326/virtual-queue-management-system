import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

const String baseUrl = "http://192.168.111.49:5000";

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Queue System',
      theme: ThemeData(
        primarySwatch: Colors.indigo,
        scaffoldBackgroundColor: Colors.grey[100],
      ),
      home: LoginPage(),
    );
  }
}

//////////////////// LOGIN ////////////////////

class LoginPage extends StatelessWidget {
  final TextEditingController nameController = TextEditingController();
  final TextEditingController adminPass = TextEditingController();

  LoginPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        width: double.infinity,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF36D1DC), Color(0xFF5B86E5)],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: Column(
          children: [
            const SizedBox(height: 80),
            const Icon(Icons.blur_circular, size: 80, color: Colors.white),
            const Text("Queue System",
                style: TextStyle(color: Colors.white, fontSize: 22)),

            const SizedBox(height: 40),

            Container(
              margin: const EdgeInsets.all(20),
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(25),
              ),
              child: Column(
                children: [
                  TextField(
                    controller: nameController,
                    decoration:
                    const InputDecoration(labelText: "Enter Name"),
                  ),
                  const SizedBox(height: 20),

                  ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.indigo,
                      minimumSize: const Size(double.infinity, 50),
                    ),
                    onPressed: () {
                      if (nameController.text.isNotEmpty) {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) =>
                                CustomerPage(nameController.text),
                          ),
                        );
                      }
                    },
                    child: const Text("Continue",
                        style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold)),
                  ),

                  const SizedBox(height: 10),

                  TextButton(
                    onPressed: () {
                      showDialog(
                        context: context,
                        builder: (_) => AlertDialog(
                          title: const Text("Admin Login"),
                          content: TextField(
                            controller: adminPass,
                            obscureText: true,
                            decoration: const InputDecoration(
                                labelText: "Enter Password"),
                          ),
                          actions: [
                            ElevatedButton(
                              onPressed: () {
                                if (adminPass.text == "admin123") {
                                  Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                        builder: (_) =>
                                        const AdminPage()),
                                  );
                                }
                              },
                              child: const Text("Login"),
                            )
                          ],
                        ),
                      );
                    },
                    child: const Text("Admin Login"),
                  )
                ],
              ),
            )
          ],
        ),
      ),
    );
  }
}

//////////////////// CUSTOMER ////////////////////

class CustomerPage extends StatefulWidget {
  final String name;
  const CustomerPage(this.name, {super.key});

  @override
  State<CustomerPage> createState() => _CustomerPageState();
}

class _CustomerPageState extends State<CustomerPage> {
  String priority = "Normal";
  Map<String, dynamic>? tokenData;
  TextEditingController cancelController = TextEditingController();

  Future<void> joinQueue() async {
    var res = await http.get(Uri.parse(
        "$baseUrl/join?name=${widget.name}&priority=$priority"));

    var data = jsonDecode(res.body);

    setState(() {
      tokenData = data;
    });
  }

  Future<void> cancelToken() async {
    var res = await http.get(
        Uri.parse("$baseUrl/cancel?token=${cancelController.text}"));

    var data = jsonDecode(res.body);

    setState(() {
      tokenData = null;
    });

    ScaffoldMessenger.of(context)
        .showSnackBar(SnackBar(content: Text(data["message"])));
  }

  Widget queueAnimation(int ahead) {
    return Column(
      children: [
        const Text("YOU ARE HERE",
            style: TextStyle(fontWeight: FontWeight.bold)),

        const SizedBox(height: 10),

        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(ahead + 1, (index) {
            bool isUser = index == ahead;

            return AnimatedContainer(
              duration: const Duration(milliseconds: 400),
              margin: const EdgeInsets.symmetric(horizontal: 5),
              child: Icon(Icons.person,
                  size: 28,
                  color: isUser ? Colors.red : Colors.grey),
            );
          }),
        ),
      ],
    );
  }

  Color priorityColor(String p) {
    if (p == "Emergency") return Colors.red;
    if (p == "VIP") return Colors.purple;
    return Colors.green;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Virtual Queue System")),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Text("[ Virtual Queue System ]",
                style: TextStyle(
                    fontSize: 20, fontWeight: FontWeight.bold)),

            const SizedBox(height: 20),

            TextField(
              enabled: false,
              decoration: InputDecoration(
                prefixIcon: const Icon(Icons.person),
                hintText: widget.name,
                border:
                OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),

            const SizedBox(height: 15),

            DropdownButtonFormField(
              value: priority,
              items: ["Normal", "VIP", "Emergency"]
                  .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                  .toList(),
              onChanged: (v) => setState(() => priority = v!),
              decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  labelText: "🎯 Priority"),
            ),

            const SizedBox(height: 15),

            ElevatedButton(
              onPressed: joinQueue,
              child: const Text("🚀 Join Queue"),
            ),

            const SizedBox(height: 20),

            if (tokenData != null) ...[
              queueAnimation(tokenData!["ahead"]),

              const SizedBox(height: 20),

              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: priorityColor(tokenData!["priority"]),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text("#${tokenData!["token"]}  ${tokenData!["name"]}",
                        style: const TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.bold)),
                    Text("⏳ Wait: ${tokenData!["wait_time"]} mins",
                        style: const TextStyle(color: Colors.white)),
                    Text("👥 Ahead: ${tokenData!["ahead"]}",
                        style: const TextStyle(color: Colors.white)),
                  ],
                ),
              ),
            ],

            const SizedBox(height: 30),

            const Divider(),

            const Text("Cancel Token",
                style: TextStyle(fontWeight: FontWeight.bold)),

            const SizedBox(height: 10),

            TextField(
              controller: cancelController,
              decoration: const InputDecoration(
                labelText: "Enter Token Number",
                border: OutlineInputBorder(),
              ),
            ),

            const SizedBox(height: 10),

            ElevatedButton(
              onPressed: cancelToken,
              child: const Text("🚫 Cancel Token"),
            )
          ],
        ),
      ),
    );
  }
}

//////////////////// ADMIN ////////////////////

class AdminPage extends StatefulWidget {
  const AdminPage({super.key});

  @override
  State<AdminPage> createState() => _AdminPageState();
}

class _AdminPageState extends State<AdminPage> {
  Map<String, dynamic>? current;

  List<Map<String, dynamic>> servedList = [];
  List<dynamic> searchResults = [];

  TextEditingController searchController = TextEditingController();

  bool isQueueEmpty = false;

  // ▶ SERVE NEXT
  Future<void> serveNext() async {
    var res = await http.get(Uri.parse("$baseUrl/serve"));
    var data = jsonDecode(res.body);

    setState(() {
      // If queue empty
      if (data["message"] == "Queue is empty") {
        isQueueEmpty = true;
        return;
      }

      // Move previous to served list
      if (current != null && current!["token"] != null) {
        servedList.insert(0, {
          "token": current!["token"],
          "name": current!["name"],
        });
      }

      current = data;
    });
  }

  // 🔍 SEARCH
  Future<void> searchCustomer(String query) async {
    if (query.isEmpty) {
      setState(() => searchResults = []);
      return;
    }

    var res =
    await http.get(Uri.parse("$baseUrl/search?prefix=$query"));

    var data = jsonDecode(res.body);

    setState(() {
      searchResults = data["results"];
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("⚙️ Admin Panel")),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [

            // 🔍 SEARCH BAR
            TextField(
              controller: searchController,
              onChanged: searchCustomer,
              decoration: InputDecoration(
                hintText: "Search Customer",
                prefixIcon: const Icon(Icons.search),
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12)),
              ),
            ),

            const SizedBox(height: 10),

            // 🔍 SEARCH RESULTS
            if (searchResults.isNotEmpty)
              Container(
                height: 100,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: ListView(
                  children: searchResults
                      .map((e) => ListTile(
                    leading: const Icon(Icons.person),
                    title: Text(e),
                  ))
                      .toList(),
                ),
              ),

            const SizedBox(height: 20),

            // ▶ SERVE BUTTON
            ElevatedButton.icon(
              onPressed: isQueueEmpty ? null : serveNext,
              icon: const Icon(Icons.play_arrow),
              label: const Text("Serve Next"),
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(double.infinity, 50),
              ),
            ),

            const SizedBox(height: 20),

            // 🟢 CURRENT SERVING
            if (current != null && current!["token"] != null)
              Card(
                color: Colors.green[100],
                elevation: 4,
                child: ListTile(
                  leading: const Icon(Icons.campaign,
                      color: Colors.green),
                  title: const Text("Now Serving",
                      style: TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text(
                    "Token ${current!["token"]} → ${current!["name"]}",
                    style: const TextStyle(fontSize: 16),
                  ),
                ),
              ),

            const SizedBox(height: 10),

            const Align(
              alignment: Alignment.centerLeft,
              child: Text("✔ Served History",
                  style: TextStyle(
                      fontWeight: FontWeight.bold, fontSize: 16)),
            ),

            const SizedBox(height: 10),

            // 📜 SERVED LIST (SCROLL)
            Expanded(
              child: servedList.isEmpty
                  ? const Center(child: Text("No customers served yet"))
                  : ListView.builder(
                itemCount: servedList.length,
                itemBuilder: (context, index) {
                  var item = servedList[index];

                  return Card(
                    child: ListTile(
                      leading: const Icon(Icons.check_circle,
                          color: Colors.grey),
                      title: Text(
                          "Token ${item["token"]} → ${item["name"]}"),
                      subtitle: const Text("Served"),
                    ),
                  );
                },
              ),
            )
          ],
        ),
      ),
    );
  }
}