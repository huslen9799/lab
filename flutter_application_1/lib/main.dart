import 'dart:math';
import 'package:flutter/material.dart';

void main() => runApp(DemoApp());

class DemoApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorSchemeSeed: Colors.deepPurple,
      ),
      home: HomePage(),
    );
  }
}

// ============================================================================
// HOMEPAGE — modern gradient + card menu
// ============================================================================
class HomePage extends StatelessWidget {
  final List<Map<String, dynamic>> demos = [
    {"title": "SliverAppBar", "page": SliverDemo(), "icon": Icons.expand},
    {"title": "GestureDetector", "page": GestureDemo(), "icon": Icons.touch_app},
    {"title": "Draggable + DragTarget", "page": DragDemo(), "icon": Icons.drag_indicator},
    {"title": "FutureBuilder", "page": FutureDemo(), "icon": Icons.timelapse},
    {"title": "StreamBuilder", "page": StreamDemo(), "icon": Icons.stream},
    {"title": "ActionsDemo", "page": HumanAnimationDemo(), "icon": Icons.animation},
    {"title": "AnimationController", "page": AnimationControllerDemo(), "icon": Icons.play_circle},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "7 Function Demo",
          style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
        backgroundColor: Colors.deepPurple,
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Colors.deepPurple, Colors.blue],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: demos.length,
          itemBuilder: (context, i) {
            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 8),
              child: InkWell(
                borderRadius: BorderRadius.circular(20),
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => demos[i]["page"]),
                  );
                },
                child: Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Colors.white70, Colors.white],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.15),
                        blurRadius: 12,
                        offset: const Offset(2, 4),
                      )
                    ],
                  ),
                  child: Row(
                    children: [
                      Icon(demos[i]["icon"], size: 32, color: Colors.deepPurple),
                      const SizedBox(width: 20),
                      Text(
                        demos[i]["title"],
                        style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                      ),
                      const Spacer(),
                      const Icon(Icons.arrow_forward_ios, color: Colors.black54)
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}

// ============================================================================
// 1. SLIVER APP BAR DEMO
// ============================================================================
class SliverDemo extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 240,
            pinned: true,
            backgroundColor: Colors.deepPurple,
            flexibleSpace: FlexibleSpaceBar(
              title: const Text(
                "SliverAppBar",
                style: TextStyle(shadows: [Shadow(blurRadius: 6, color: Colors.black)]),
              ),
              background: Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    colors: [Colors.deepPurple, Colors.indigo, Colors.blue],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                ),
              ),
            ),
          ),
          SliverList(
            delegate: SliverChildBuilderDelegate(
              (_, i) => ListTile(title: Text("Item $i")),
              childCount: 20,
            ),
          )
        ],
      ),
    );
  }
}

// ============================================================================
// 2. GESTURE DETECTOR DEMO
// ============================================================================
class GestureDemo extends StatefulWidget {
  @override
  _GestureDemoState createState() => _GestureDemoState();
}

class _GestureDemoState extends State<GestureDemo> {
  Color color = Colors.teal;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("GestureDetector")),
      body: Center(
        child: GestureDetector(
          onTap: () {
            setState(() {
              color = color == Colors.teal ? Colors.pinkAccent : Colors.teal;
            });
          },
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 350),
            width: 150,
            height: 150,
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(25),
              boxShadow: [
                BoxShadow(color: color.withOpacity(0.5), blurRadius: 15, spreadRadius: 3),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// ============================================================================
// 3. DRAGGABLE + DRAGTARGET DEMO
// ============================================================================
class DragDemo extends StatefulWidget {
  @override
  _DragDemoState createState() => _DragDemoState();
}

class _DragDemoState extends State<DragDemo> {
  bool accepted = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Drag & Drop")),
      body: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          Draggable(
            data: "ball",
            feedback: CircleAvatar(
              radius: 35,
              backgroundColor: Colors.amber.shade600,
            ),
            child: const CircleAvatar(
              radius: 35,
              backgroundColor: Colors.indigo,
            ),
          ),
          DragTarget(
            onAccept: (value) {
              setState(() {
                accepted = true;
              });
            },
            builder: (_, __, ___) {
              return Container(
                width: 110,
                height: 110,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: accepted ? [Colors.green, Colors.lightGreen] : [Colors.greenAccent, Colors.green],
                  ),
                  borderRadius: BorderRadius.circular(25),
                  boxShadow: [
                    BoxShadow(color: Colors.green.withOpacity(0.4), blurRadius: 10),
                  ],
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}

// ============================================================================
// 4. FUTURE BUILDER DEMO
// ============================================================================
class FutureDemo extends StatelessWidget {
  Future<String> load() async {
    await Future.delayed(const Duration(seconds: 2));
    return "Амжилттай ачааллаа!";
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("FutureBuilder")),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Colors.pink, Colors.deepPurple],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Center(
          child: FutureBuilder(
            future: load(),
            builder: (_, snapshot) {
              if (!snapshot.hasData) {
                return const CircularProgressIndicator(color: Colors.white);
              }

              return AnimatedOpacity(
                duration: const Duration(milliseconds: 600),
                opacity: 1,
                child: Text(
                  snapshot.data!,
                  style: const TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              );
            },
          ),
        ),
      ),
    );
  }
}

// ============================================================================
// 5. STREAM BUILDER DEMO
// ============================================================================
class StreamDemo extends StatelessWidget {
  Stream<int> counter() async* {
    for (int i = 0; i < 9999; i++) {
      await Future.delayed(const Duration(milliseconds: 400));
      yield i;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("StreamBuilder")),
      body: Center(
        child: StreamBuilder<int>(
          stream: counter(),
          builder: (_, snapshot) {
            return AnimatedDefaultTextStyle(
              duration: const Duration(milliseconds: 300),
              style: TextStyle(
                fontSize: 50,
                fontWeight: FontWeight.bold,
                color: Colors.orangeAccent,
                shadows: [Shadow(color: Colors.black26, blurRadius: 8)],
              ),
              child: Text("${snapshot.data ?? 0}"),
            );
          },
        ),
      ),
    );
  }
}

// ============================================================================
// 6. DOG ANIMATION DEMO — Interactive Hero + Speed + Color Adjust
// ============================================================================
class HumanAnimationDemo extends StatefulWidget {
  @override
  _HumanAnimationDemoState createState() => _HumanAnimationDemoState();
}

class _HumanAnimationDemoState extends State<HumanAnimationDemo>
    with SingleTickerProviderStateMixin {
  late AnimationController controller;
  late Animation<double> jump, tailSwing, legSwing;
  String action = "Idle";
  double speed = 1.0;
  Color bodyColor = Colors.orange;
  Color tailColor = Colors.orangeAccent;

  @override
  void initState() {
    super.initState();
    controller = AnimationController(vsync: this, duration: const Duration(seconds: 2));
    setupAnimations();
    controller.repeat(reverse: true);
  }

  void setupAnimations() {
    jump = Tween<double>(begin: 0, end: -30).animate(
      CurvedAnimation(parent: controller, curve: Curves.easeInOut),
    );
    tailSwing = Tween<double>(begin: -25, end: 25).animate(
      CurvedAnimation(parent: controller, curve: Curves.easeInOut),
    );
    legSwing = Tween<double>(begin: -20, end: 20).animate(
      CurvedAnimation(parent: controller, curve: Curves.easeInOut),
    );
  }

  void setAction(String newAction) {
    setState(() {
      action = newAction;
      controller.reset();
      if (["Run", "Walk", "Jump"].contains(newAction)) {
        controller.repeat(reverse: true);
      } else {
        controller.stop();
      }
    });
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  Widget buildDog() {
    return AnimatedBuilder(
      animation: controller,
      builder: (_, child) {
        double offsetY = 0;
        double tailAngle = 0;
        double frontLeg = 0;
        double backLeg = 0;

        switch (action) {
          case "Jump":
            offsetY = jump.value;
            tailAngle = tailSwing.value;
            frontLeg = legSwing.value;
            backLeg = -legSwing.value;
            break;
          case "Run":
            tailAngle = tailSwing.value;
            frontLeg = legSwing.value * 1.5;
            backLeg = -legSwing.value * 1.5;
            break;
          case "Walk":
            tailAngle = tailSwing.value / 2;
            frontLeg = legSwing.value;
            backLeg = -legSwing.value;
            break;
        }

        return Transform.translate(
          offset: Offset(0, offsetY),
          child: Hero(
            tag: 'dog-hero',
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Head
                Container(width: 50, height: 50, decoration: BoxDecoration(color: Colors.brown, shape: BoxShape.circle)),
                // Body
                Container(width: 70, height: 40, color: bodyColor),
                const SizedBox(height: 4),
                // Legs
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Transform.rotate(angle: frontLeg * pi / 180, child: Container(width: 10, height: 40, color: Colors.brown)),
                    Transform.rotate(angle: backLeg * pi / 180, child: Container(width: 10, height: 40, color: Colors.brown)),
                  ],
                ),
                const SizedBox(height: 4),
                // Tail
                Transform.rotate(angle: tailAngle * pi / 180, alignment: Alignment.topLeft, child: Container(width: 10, height: 30, color: tailColor)),
              ],
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Interactive Dog Animation"), backgroundColor: Colors.deepPurple),
      backgroundColor: Colors.black,
      body: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          buildDog(),
          const SizedBox(height: 20),
          // Action buttons
          Wrap(
            spacing: 8,
            children: ["Idle", "Jump", "Run", "Walk"].map((e) {
              return ElevatedButton(
                onPressed: () => setAction(e),
                child: Text(e),
                style: ElevatedButton.styleFrom(backgroundColor: Colors.grey[800]),
              );
            }).toList(),
          ),
          const SizedBox(height: 20),
          // Speed slider
          Column(
            children: [
              const Text("Speed", style: TextStyle(color: Colors.white)),
              Slider(
                value: speed,
                min: 0.2,
                max: 3.0,
                divisions: 28,
                label: speed.toStringAsFixed(1),
                onChanged: (val) {
                  setState(() {
                    speed = val;
                    controller.duration = Duration(milliseconds: (2000 ~/ speed));
                    if (["Run","Walk","Jump"].contains(action)) controller.repeat(reverse: true);
                  });
                },
              ),
            ],
          ),
          const SizedBox(height: 10),
          // Color buttons
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              ElevatedButton(
                  onPressed: () => setState(() => bodyColor = Colors.orange),
                  child: const Text("Body Orange")),
              const SizedBox(width: 8),
              ElevatedButton(
                  onPressed: () => setState(() => bodyColor = Colors.purple),
                  child: const Text("Body Purple")),
              const SizedBox(width: 8),
              ElevatedButton(
                  onPressed: () => setState(() => tailColor = Colors.orangeAccent),
                  child: const Text("Tail Orange")),
              const SizedBox(width: 8),
              ElevatedButton(
                  onPressed: () => setState(() => tailColor = Colors.pinkAccent),
                  child: const Text("Tail Pink")),
            ],
          )
        ],
      ),
    );
  }
}



// ============================================================================
// 7. ANIMATION CONTROLLER DEMO
// ============================================================================
class AnimationControllerDemo extends StatefulWidget {
  @override
  _AnimationControllerDemoState createState() =>
      _AnimationControllerDemoState();
}

class _AnimationControllerDemoState extends State<AnimationControllerDemo>
    with SingleTickerProviderStateMixin {
  late AnimationController controller;
  late Animation<double> anim;

  @override
  void initState() {
    super.initState();

    controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 1),
    );

    anim = CurvedAnimation(
      parent: controller,
      curve: Curves.easeInOut,
    );

    controller.repeat(reverse: true);
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("AnimationController Demo")),
      body: Center(
        child: AnimatedBuilder(
          animation: anim,
          builder: (_, child) {
            return Transform.scale(
              scale: anim.value * 1.2 + 0.8,
              child: Container(
                width: 130,
                height: 130,
                decoration: BoxDecoration(
                  color: Colors.deepPurpleAccent,
                  borderRadius: BorderRadius.circular(25),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.deepPurpleAccent.withOpacity(0.5),
                      blurRadius: 10 + 30 * anim.value,
                      spreadRadius: 5 * anim.value,
                    )
                  ],
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}
