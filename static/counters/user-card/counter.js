
const UserCardCounter = {
	init() {
		UserCardPanel.init();
		app.root.append(UserCardPanel.container);
		UserCardPanel.container.classList.add("full-size");

		app.onCommand("getSettings", (settings) => {
			UserCardPanel.settings(settings);
		});
	}
}

app.registerCounter(UserCardCounter);
