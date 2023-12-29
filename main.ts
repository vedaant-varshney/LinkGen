import { App, Editor, MarkdownView, Modal, Notice, Plugin, PluginSettingTab, Setting, Menu } from 'obsidian';
// TODO: Remember to rename these classes and interfaces!

interface MyPluginSettings {
	mySetting: string;
}

const DEFAULT_SETTINGS: MyPluginSettings = {
	mySetting: 'default'
}

export default class MyPlugin extends Plugin {
	settings: MyPluginSettings;

	async onload() {
		await this.loadSettings();

		// Creates Document Tag Section
		this.addCommand({
			id: "generate-tag-section",
			name: "Generate Tags",
			editorCallback: (editor: Editor, view: MarkdownView) => {
				console.log(editor.lastLine());
				console.log(editor.getValue());
				editor.setValue(editor.getValue() + "\n\n---\n### Tag List\n\n\n---\n")
			}
		});

		// Inserts Tag based on selection
		this.addCommand({
			id: "insert-tag",
			name: "Insert Tag",
			hotkeys: [{ modifiers: ["Mod", "Alt"], key: "t" }],
			editorCallback: (editor: Editor, view: MarkdownView) => {
				// Line for tag insert
				let tagline = 0;
				for (let i = 0; i < editor.lastLine(); ++i) {
					if (editor.getLine(i) == "### Tag List") {
						tagline = i + 1;
						break;
					}
				}
				const currentSelection = editor.getSelection()
				editor.setLine(tagline, `#${currentSelection.toLowerCase()} ` + editor.getLine(tagline))

			}
		});


		// TODO: Create option for suggesting top 5 tags

		// This adds a settings tab so the user can configure various aspects of the plugin
		this.addSettingTab(new SampleSettingTab(this.app, this));

		// If the plugin hooks up any global DOM events (on parts of the app that doesn't belong to this plugin)
		// Using this function will automatically remove the event listener when this plugin is disabled.
		this.registerDomEvent(document, 'click', (evt: MouseEvent) => {
			// console.log('click', evt);
		});

		// When registering intervals, this function will automatically clear the interval when the plugin is disabled.
		this.registerInterval(window.setInterval(() => console.log('setInterval'), 5 * 60 * 1000));
	}

	onunload() {

	}

	async loadSettings() {
		this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
	}

	async saveSettings() {
		await this.saveData(this.settings);
	}
}


class SampleSettingTab extends PluginSettingTab {
	plugin: MyPlugin;

	constructor(app: App, plugin: MyPlugin) {
		super(app, plugin);
		this.plugin = plugin;
	}

	display(): void {
		const { containerEl } = this;

		containerEl.empty();

		new Setting(containerEl)
			.setName('Setting #1')
			.setDesc('It\'s a secret')
			.addText(text => text
				.setPlaceholder('Enter your secret')
				.setValue(this.plugin.settings.mySetting)
				.onChange(async (value) => {
					this.plugin.settings.mySetting = value;
					await this.plugin.saveSettings();
				}));
	}
}
