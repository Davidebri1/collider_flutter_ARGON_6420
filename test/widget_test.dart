import 'package:material_ui/material_ui.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:collider_flutter/main.dart';

void main() {
  testWidgets('Collider VisionOS Architecture, Consensus Row, Permanent Nav Bar & History Tests', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(2400, 2400);
    tester.view.devicePixelRatio = 2.0;
    addTearDown(tester.view.resetPhysicalSize);

    await tester.pumpWidget(const ColliderApp());
    await tester.pump(const Duration(milliseconds: 300));

    // 1. Composer is tucked by default; summon it through the bottom nav.
    expect(find.textContaining('Compare whole life vs term life insurance for a young family.'), findsNothing);
    await tester.tap(find.byTooltip('Compose / Home'));
    await tester.pump(const Duration(milliseconds: 300));
    expect(find.textContaining('Compare whole life vs term life insurance for a young family.'), findsAtLeast(1));

    // 2. Verify Pinned Consensus Preview Row (1 line consensus summary, not truncated)
    expect(find.textContaining('Consensus'), findsAtLeast(1));
    expect(find.textContaining('Term life provides maximum protection per dollar; invest the surplus independently.'), findsOneWidget);

    // 3. Verify Active Ticker Model Pills (Directly visible in Desktop 2-Column Grid)
    expect(find.text('GPT-5 Nano'), findsOneWidget);
    expect(find.text('Gemini 3.6 Flash Lite'), findsOneWidget);
    expect(find.text('Claude 3.7 Sonnet'), findsOneWidget);

    // 4. Verify permanent bottom nav is the 3-icon contract.
    expect(find.byTooltip('Compose / Home'), findsOneWidget);
    expect(find.byTooltip('Settings'), findsOneWidget);
    expect(find.byTooltip('Apps'), findsOneWidget);

    // 4b. Verify AI Chat contextual side nav owns history/model controls.
    expect(find.byTooltip('Local History'), findsOneWidget);
    expect(find.byTooltip('Global History'), findsOneWidget);
    expect(find.byTooltip('Consensus History'), findsOneWidget);
    expect(find.byTooltip('New conversation'), findsOneWidget);

    // 5. Test Inline Accordion Expansion
    await tester.tap(find.text('GPT-5 Nano'));
    await tester.pump(const Duration(milliseconds: 300));

    // Verify local tools ribbon exists (Search, Local Files, Local History, Copy, Browser Jump, Collapse)
    expect(find.byTooltip('Search conversation'), findsOneWidget);
    expect(find.byTooltip('Local model files & attachments'), findsOneWidget);
    expect(find.byTooltip('Local model history'), findsOneWidget);
    expect(find.byTooltip('Copy answer'), findsOneWidget);

    // 7. Test In-Line Isolated Message Branching
    final inlineInput = find.widgetWithText(TextField, "Reply specifically to GPT-5 Nano...");
    expect(inlineInput, findsOneWidget);
    await tester.enterText(inlineInput, 'Explain index funds vs cash value');
    await tester.pump(const Duration(milliseconds: 100));

    final sendBtn = find.byIcon(Icons.send_rounded).first;
    await tester.ensureVisible(sendBtn);
    await tester.pump(const Duration(milliseconds: 100));
    await tester.tap(sendBtn, warnIfMissed: false);
    await tester.pump(const Duration(milliseconds: 300));

    expect(find.text('Isolated'), findsAtLeast(1));

    // 8. Test Local Model History Popup Pane
    final localHistoryBtn = find.byTooltip('Local model history');
    await tester.ensureVisible(localHistoryBtn);
    await tester.pump(const Duration(milliseconds: 200));
    await tester.tap(localHistoryBtn, warnIfMissed: false);
    await tester.pump(const Duration(milliseconds: 300));

    expect(find.text('G5N History'), findsOneWidget);
    expect(find.byType(TextField), findsAtLeast(1));

    // Click on session in local history to load & expand immediately
    final localSessionItem = find.text('Family Estate Will & Trust Directives');
    expect(localSessionItem, findsOneWidget);
    await tester.tap(localSessionItem);
    await tester.pump(const Duration(milliseconds: 300));

    // Pane should be closed, session loaded, and pill expanded
    expect(find.text('G5N History'), findsNothing);
    expect(find.textContaining('Structuring testamentary wills'), findsOneWidget);

    // 9. Test Apps Popup Pane (Summons to middle neutral area, blurred background, 7 icons)
    final appsNavBtn = find.byTooltip('Apps');
    await tester.tap(appsNavBtn);
    await tester.pump(const Duration(milliseconds: 300));

    expect(find.byTooltip('Smart Gen'), findsOneWidget);
    expect(find.byTooltip('Discover Market'), findsOneWidget);
    expect(find.byTooltip('Theme Gallery'), findsOneWidget);
    expect(find.byTooltip('Premium Marketplace'), findsOneWidget);
    expect(find.byTooltip('Files'), findsOneWidget);
    expect(find.byTooltip('Music Player'), findsOneWidget);
    expect(find.byTooltip('Browser'), findsOneWidget);

    // Escape via close icon
    final appsCloseBtn = find.byIcon(Icons.close_rounded).first;
    await tester.tap(appsCloseBtn);
    await tester.pump(const Duration(milliseconds: 300));
    expect(find.byTooltip('Smart Gen'), findsNothing);

    // 10. Test Global Conversation History in contextual AI Chat side nav.
    final globalHistoryTab = find.byTooltip('Global History');
    await tester.tap(globalHistoryTab);
    await tester.pump(const Duration(milliseconds: 300));

    expect(find.text('Winter Home Weatherization & Heat Pump Efficiency'), findsOneWidget);

    // Click on session to load and expand immediately
    await tester.tap(find.text('Winter Home Weatherization & Heat Pump Efficiency'));
    await tester.pump(const Duration(milliseconds: 300));

    // Tapping a session closes side panes and lands on the expanded model conversation.
    expect(find.textContaining('Practical steps to minimize home heating loss'), findsAtLeast(1));
  });

  testWidgets('Collider Mobile Responsive Viewport: Tucked SideNav and Sessions trigger', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(393 * 3, 852 * 3);
    tester.view.devicePixelRatio = 3.0;
    addTearDown(tester.view.resetPhysicalSize);

    await tester.pumpWidget(const ColliderApp());
    await tester.pump(const Duration(milliseconds: 300));

    // On mobile, the floating History trigger is visible
    expect(find.text('History'), findsOneWidget);

    // Tap History trigger to open mobile side nav
    await tester.tap(find.text('History'));
    await tester.pump(const Duration(milliseconds: 300));

    // Contextual side nav tabs are now active and on screen
    expect(find.byTooltip('Global History'), findsOneWidget);
    await tester.tap(find.byTooltip('Global History'));
    await tester.pump(const Duration(milliseconds: 300));
    expect(find.text('Winter Home Weatherization & Heat Pump Efficiency'), findsOneWidget);
  });

  testWidgets('Collider Premium Theme Marketplace (Node 1-3 CoverFlow) & Theme Detail View (Node 417-15864)', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(2400, 2400);
    tester.view.devicePixelRatio = 2.0;
    addTearDown(tester.view.resetPhysicalSize);

    await tester.pumpWidget(const ColliderApp());
    await tester.pump(const Duration(milliseconds: 300));

    // 1. Open Apps Popup Pane
    await tester.tap(find.byTooltip('Apps'));
    await tester.pump(const Duration(milliseconds: 300));

    // 2. Tap Premium Marketplace to open 3D CoverFlow Marketplace (Node 1-3)
    await tester.tap(find.byTooltip('Premium Marketplace'));
    await tester.pump(const Duration(milliseconds: 300));

    // 3. Verify CoverFlow Top Search Bar & Artist Query Subtitle
    expect(find.text('Search'), findsOneWidget);
    expect(find.textContaining('Search for artists like "Beatles", "Drake", "Taylor Swift"'), findsOneWidget);

    // 4. Verify 3D CoverFlow Center Card & Track Info
    expect(find.text('Drivers License'), findsOneWidget);
    expect(find.text('Olivia Rodrigo'), findsOneWidget);
    expect(find.text('from SOUR (2021)'), findsOneWidget);

    // 5. Verify Glowing Center Play Button & "Tap to play" Affordance
    expect(find.byIcon(Icons.play_arrow_rounded), findsAtLeast(1));
    expect(find.text('Tap to play'), findsOneWidget);
    expect(find.text('Set Active Wallpaper'), findsOneWidget);

    // 6. Test Play/Pause toggle
    await tester.tap(find.bySemanticsLabel('Play Preview'));
    await tester.pump(const Duration(milliseconds: 200));
    expect(find.text('Playing audio preview'), findsOneWidget);
    expect(find.byIcon(Icons.pause_rounded), findsAtLeast(1));

    // 7. Escape CoverFlow view via Close Button
    final closeBtn = find.byIcon(Icons.close_rounded).first;
    await tester.tap(closeBtn);
    await tester.pump(const Duration(milliseconds: 300));
    expect(find.text('from SOUR (2021)'), findsNothing);

    // 8. Test opening Theme Detail (Node 417-15864) from regular Theme Gallery
    await tester.tap(find.byTooltip('Apps'));
    await tester.pump(const Duration(milliseconds: 300));
    await tester.tap(find.byTooltip('Theme Gallery'));
    await tester.pump(const Duration(milliseconds: 300));
    expect(find.text('Wallpaper Gallery'), findsOneWidget);

    // Switch to 4K Live tier
    await tester.tap(find.text('✦ 4K Live'));
    await tester.pump(const Duration(milliseconds: 300));

    // Click on "5 Curated Tracks >" to open ThemeMarketplaceDetailView
    expect(find.text('5 Curated Tracks >'), findsOneWidget);
    await tester.tap(find.text('5 Curated Tracks >'));
    await tester.pump(const Duration(milliseconds: 300));

    // Verify 5 curated soundscape tracks in detail view
    expect(find.text('Curated Soundscape'), findsOneWidget);
    expect(find.text('5 Tracks Bundled'), findsOneWidget);
    expect(find.text('Bridge Over Constellations'), findsOneWidget);

    // Return to selector via Swipe-Down / Selector button
    await tester.tap(find.text('Selector'));
    await tester.pump(const Duration(milliseconds: 300));
    expect(find.text('Curated Soundscape'), findsNothing);
    expect(find.text('Wallpaper Gallery'), findsOneWidget);
  });

  testWidgets('Collider Contextual Side Nav Adaptation Across Work Surfaces & Adequate Warning Consent Dialog', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(2400, 2400);
    tester.view.devicePixelRatio = 2.0;
    addTearDown(tester.view.resetPhysicalSize);

    await tester.pumpWidget(const ColliderApp());
    await tester.pump(const Duration(milliseconds: 300));

    // 1. Initial State: AI Chat contextual side nav is active
    expect(find.text('AI Chat'), findsOneWidget);
    expect(find.byTooltip('Global History'), findsOneWidget);

    // 2. Open Apps overlay and tap Smart Gen to open Smart Gen
    await tester.tap(find.byTooltip('Apps'));
    await tester.pump(const Duration(milliseconds: 300));
    await tester.tap(find.byTooltip('Smart Gen'));
    await tester.pump(const Duration(milliseconds: 300));

    // 3. Smart Gen Workspace is now active
    expect(find.text('Smart Gen Workspace'), findsOneWidget);

    // 4. Contextual Side Nav has adapted to Smart Gen
    expect(find.text('SMART GEN SUITE'), findsOneWidget);
    expect(find.text('BOARD VIEWS'), findsOneWidget);
    expect(find.text('Kanban'), findsOneWidget);
    expect(find.text('Calendar'), findsOneWidget);

    // 5. Trigger Adequate Warning / User Consent dialog by attempting to navigate Home
    await tester.tap(find.byTooltip('Compose / Home'));
    await tester.pump(const Duration(milliseconds: 300));

    // Warning / User Consent dialog must appear focusing on warning and consent
    expect(find.text('Unsaved Changes'), findsOneWidget);
    expect(find.textContaining('preserved in memory'), findsOneWidget);
    expect(find.text('Keep Editing'), findsOneWidget);
    expect(find.text('Leave View'), findsOneWidget);

    // 6. Test 'Keep Editing' action: cancels transition and remains on Smart Gen
    await tester.tap(find.text('Keep Editing'));
    await tester.pump(const Duration(milliseconds: 300));
    expect(find.text('Unsaved Changes'), findsNothing);
    expect(find.text('Smart Gen Workspace'), findsOneWidget);

    // 7. Trigger Consent dialog again and test 'Leave View' action
    await tester.tap(find.byTooltip('Compose / Home'));
    await tester.pump(const Duration(milliseconds: 300));
    expect(find.text('Unsaved Changes'), findsOneWidget);

    await tester.tap(find.text('Leave View'));
    await tester.pump(const Duration(milliseconds: 300));

    // Smart Gen is closed, home composer is summoned, side nav returned to AI Chat
    expect(find.text('Smart Gen Workspace'), findsNothing);
    expect(find.text('AI Chat'), findsOneWidget);
  });
}
