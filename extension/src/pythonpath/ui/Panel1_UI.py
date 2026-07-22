# -*- coding: utf-8 -*-
#!/usr/bin/env python

# =============================================================================
#
# Dialog implementation generated from a XDL file.
#
# Created: Sun Nov 23 01:30:57 2025
#      by: unodit 0.8.0
#
# WARNING! All changes made in this file will be overwritten
#          if the file is generated again!
#
# =============================================================================

import uno
import unohelper
from com.sun.star.awt import XActionListener
from com.sun.star.awt import XWindowListener
from com.sun.star.task import XJobExecutor
from ui_logic.settings import Settings
from com.sun.star.awt import XActionListener, XItemListener, XWindowListener, XFocusListener

# Placeholder constants
PROMPT_PLACEHOLDER = "Type your prompt here"
PROMPT_NAME_PLACEHOLDER = "Prompt name"

class Panel1_UI(unohelper.Base, XActionListener, XItemListener, XFocusListener, XWindowListener, XJobExecutor):
    """
    Class documentation...
    """

    def __init__(
        self, ctx=uno.getComponentContext(), dialog=None, settings: Settings = None
    ):
        self.LocalContext = ctx
        self.dlg = dialog
        self.settings = settings
        self.ServiceManager = self.LocalContext.ServiceManager
        self.Toolkit = self.ServiceManager.createInstanceWithContext(
            "com.sun.star.awt.ExtToolkit", self.LocalContext
        )

        # -----------------------------------------------------------
        #               Create dialog and insert controls
        # -----------------------------------------------------------

        # --------------create dialog container and set model and properties
        self.DialogContainer = self.dlg
        self.DialogModel = self.ServiceManager.createInstance(
            "com.sun.star.awt.UnoControlDialogModel"
        )
        self.DialogContainer.setModel(self.DialogModel)
        self.DialogModel.Name = "LlmDialog"
        self.DialogModel.PositionX = "204"
        self.DialogModel.PositionY = "117"
        self.DialogModel.Width = 156
        self.DialogModel.Height = 620
        self.DialogModel.Closeable = True
        self.DialogModel.Moveable = True

        dialogLeftPadding = 6

        # Layout constants
        BUTTON_HEIGHT = 18
        SMALL_BUTTON_WIDTH = 43
        BUTTON_GAP = 4

        # Button colour constants
        COLOR_BUTTON_DEFAULT = 0xF0F0F0
        COLOR_BUTTON_PRIMARY = 0xDDEEFF     # Light blue
        COLOR_BUTTON_SAVE = 0xE8F5E9        # Light green
        COLOR_BUTTON_DELETE = 0xFFE0E0      # Light red
        COLOR_BUTTON_SETTINGS = 0xFFF8E1    # Light yellow

        # --------- Combined Prompt Name & Dropdown ---------
        self.PromptNameCombo = self.DialogModel.createInstance("com.sun.star.awt.UnoControlComboBoxModel")
        self.PromptNameCombo.Dropdown = True
        self.PromptNameCombo.Name = "PromptNameCombo"
        self.PromptNameCombo.PositionX = dialogLeftPadding
        self.PromptNameCombo.PositionY = 8
        self.PromptNameCombo.Width = 136
        self.PromptNameCombo.Height = 15
        self.PromptNameCombo.Text = PROMPT_NAME_PLACEHOLDER
        self.DialogModel.insertByName("PromptNameCombo", self.PromptNameCombo)

        # Listen for dropdown selections AND focus changes (to clear the placeholder)
        self.DialogContainer.getControl("PromptNameCombo").addItemListener(self)
        self.DialogContainer.getControl("PromptNameCombo").addFocusListener(self)

        # --------- Prompt Management Buttons ---------
        self.NewPrompt = self.DialogModel.createInstance("com.sun.star.awt.UnoControlButtonModel")
        self.NewPrompt.Name = "NewPrompt"
        self.NewPrompt.PositionX = dialogLeftPadding
        self.NewPrompt.PositionY = self.PromptNameCombo.PositionY + 20
        self.NewPrompt.Width = SMALL_BUTTON_WIDTH
        self.NewPrompt.Height = BUTTON_HEIGHT
        self.NewPrompt.BackgroundColor = COLOR_BUTTON_PRIMARY
        self.NewPrompt.Label = "New Prompt"
        self.DialogModel.insertByName("NewPrompt", self.NewPrompt)
        self.DialogContainer.getControl("NewPrompt").addActionListener(self)
        self.DialogContainer.getControl("NewPrompt").setActionCommand("NewPrompt_OnClick")

        self.SavePrompt = self.DialogModel.createInstance("com.sun.star.awt.UnoControlButtonModel")
        self.SavePrompt.Name = "SavePrompt"
        self.SavePrompt.PositionX = dialogLeftPadding + SMALL_BUTTON_WIDTH + BUTTON_GAP
        self.SavePrompt.PositionY = self.NewPrompt.PositionY
        self.SavePrompt.Width = SMALL_BUTTON_WIDTH
        self.SavePrompt.Height = BUTTON_HEIGHT
        self.SavePrompt.BackgroundColor = COLOR_BUTTON_SAVE
        self.SavePrompt.Label = "Save Prompt"
        self.DialogModel.insertByName("SavePrompt", self.SavePrompt)
        self.DialogContainer.getControl("SavePrompt").addActionListener(self)
        self.DialogContainer.getControl("SavePrompt").setActionCommand("SavePrompt_OnClick")

        self.DeletePrompt = self.DialogModel.createInstance("com.sun.star.awt.UnoControlButtonModel")
        self.DeletePrompt.Name = "DeletePrompt"
        self.DeletePrompt.PositionX = dialogLeftPadding + (SMALL_BUTTON_WIDTH + BUTTON_GAP) * 2
        self.DeletePrompt.PositionY = self.NewPrompt.PositionY
        self.DeletePrompt.Width = SMALL_BUTTON_WIDTH
        self.DeletePrompt.Height = BUTTON_HEIGHT
        self.DeletePrompt.BackgroundColor = COLOR_BUTTON_DELETE
        self.DeletePrompt.Label = "Delete"
        self.DialogModel.insertByName("DeletePrompt", self.DeletePrompt)
        self.DialogContainer.getControl("DeletePrompt").addActionListener(self)
        self.DialogContainer.getControl("DeletePrompt").setActionCommand("DeletePrompt_OnClick")

        # --------- create an instance of Edit control, set properties ---
        self.Prompt = self.DialogModel.createInstance(
            "com.sun.star.awt.UnoControlEditModel"
        )

        self.Prompt.Name = "Prompt"
        self.Prompt.TabIndex = 0
        self.Prompt.PositionX = dialogLeftPadding
        self.Prompt.PositionY = self.NewPrompt.PositionY + 24
        self.Prompt.Width = 136
        self.Prompt.Height = 50
        self.Prompt.Text = PROMPT_PLACEHOLDER
        self.Prompt.MultiLine = True
        self.Prompt.VerticalAlign = "TOP"
        self.Prompt.AutoVScroll = True

        # inserts the control model into the dialog model
        self.DialogModel.insertByName("Prompt", self.Prompt)
        self.DialogContainer.getControl("Prompt").addFocusListener(self)

        # --------- create an instance of Button control, set properties ---
        self.Submit = self.DialogModel.createInstance(
            "com.sun.star.awt.UnoControlButtonModel"
        )

        self.Submit.Name = "Submit"
        self.Submit.TabIndex = self.Prompt.TabIndex + 1
        self.Submit.PositionX = dialogLeftPadding
        self.Submit.PositionY = self.Prompt.PositionY + 58
        self.Submit.Width = 64
        self.Submit.Height = BUTTON_HEIGHT
        self.Submit.BackgroundColor = COLOR_BUTTON_PRIMARY
        self.Submit.Label = "Submit"

        # inserts the control model into the dialog model
        self.DialogModel.insertByName("Submit", self.Submit)

        # add the action listener
        self.DialogContainer.getControl("Submit").addActionListener(self)
        self.DialogContainer.getControl("Submit").setActionCommand("Submit_OnClick")

        # --------- create an instance of RadioButton control, set properties ---
        self.SelectedTextOption = self.DialogModel.createInstance(
            "com.sun.star.awt.UnoControlRadioButtonModel"
        )

        self.SelectedTextOption.Name = "SelectedText"
        self.SelectedTextOption.TabIndex = self.Submit.TabIndex + 1
        self.SelectedTextOption.PositionX = "82"
        self.SelectedTextOption.PositionY = self.Submit.PositionY + 4
        self.SelectedTextOption.Width = 64
        self.SelectedTextOption.Height = 10
        self.SelectedTextOption.Label = "Selected Text"
        self.SelectedTextOption.State = 1

        # inserts the control model into the dialog model
        self.DialogModel.insertByName("SelectedTextOption", self.SelectedTextOption)
        self.DialogContainer.getControl("SelectedTextOption").addItemListener(self)

        # --------- create an instance of RadioButton control, set properties ---
        self.EntireDocumentOption = self.DialogModel.createInstance(
            "com.sun.star.awt.UnoControlRadioButtonModel"
        )

        self.EntireDocumentOption.Name = "EntireDocument"
        self.EntireDocumentOption.TabIndex = self.SelectedTextOption.TabIndex + 1
        self.EntireDocumentOption.PositionX = "82"
        self.EntireDocumentOption.PositionY = self.SelectedTextOption.PositionY + 11
        self.EntireDocumentOption.Width = 64
        self.EntireDocumentOption.Height = 10
        self.EntireDocumentOption.Label = "Entire Document"
        self.EntireDocumentOption.State = 0

        # inserts the control model into the dialog model
        self.DialogModel.insertByName("EntireDocumentOption", self.EntireDocumentOption)
        self.DialogContainer.getControl("EntireDocumentOption").addItemListener(self)

        # --------- NEW: Model Output Textbox ---------
        self.ModelOutputBox = self.DialogModel.createInstance(
            "com.sun.star.awt.UnoControlEditModel"
        )
        self.ModelOutputBox.Name = "ModelOutputBox"
        self.ModelOutputBox.TabIndex = self.EntireDocumentOption.TabIndex + 1
        self.ModelOutputBox.PositionX = dialogLeftPadding
        self.ModelOutputBox.PositionY = self.EntireDocumentOption.PositionY + 20
        self.ModelOutputBox.Width = 136
        self.ModelOutputBox.Height = 104
        self.ModelOutputBox.MultiLine = True
        self.ModelOutputBox.VScroll = True  # Makes it vertically scrollable
        self.ModelOutputBox.ReadOnly = True # Selectable, but cannot be typed in

        self.DialogModel.insertByName("ModelOutputBox", self.ModelOutputBox)

        self.StatusText = self.DialogModel.createInstance(
            "com.sun.star.awt.UnoControlFixedTextModel"
        )
        self.StatusText.Name = "StatusText"
        self.StatusText.PositionX = dialogLeftPadding
        self.StatusText.PositionY = self.ModelOutputBox.PositionY + 112 # Anchored below the new textbox
        self.StatusText.Width = 136
        self.StatusText.Height = 30
        self.StatusText.Label = ""
        self.StatusText.MultiLine = True

        self.DialogModel.insertByName("StatusText", self.StatusText)

        self.LinksSectionHeading = self.DialogModel.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
        self.LinksSectionHeading.Name = "LinksSectionHeading"
        self.LinksSectionHeading.PositionX = dialogLeftPadding
        self.LinksSectionHeading.PositionY = self.StatusText.PositionY + 30
        self.LinksSectionHeading.Width = 136
        self.LinksSectionHeading.Height = 10
        self.LinksSectionHeading.Label = "Links"
        self.DialogModel.insertByName("LinksSectionHeading", self.LinksSectionHeading)

        # 1. Import/Export Prompts (A button disguised as a text link)
        self.ImportExportPrompts = self.DialogModel.createInstance("com.sun.star.awt.UnoControlButtonModel")
        self.ImportExportPrompts.Name = "ImportExportPrompts"
        self.ImportExportPrompts.PositionX = dialogLeftPadding
        self.ImportExportPrompts.PositionY = self.LinksSectionHeading.PositionY + 12
        self.ImportExportPrompts.Width = 136
        self.ImportExportPrompts.Height = 14
        self.ImportExportPrompts.Label = "• Import/Export Prompts"
        self.ImportExportPrompts.Align = 0 # Left align
        self.DialogModel.insertByName("ImportExportPrompts", self.ImportExportPrompts)
        self.DialogContainer.getControl("ImportExportPrompts").addActionListener(self)
        self.DialogContainer.getControl("ImportExportPrompts").setActionCommand("ImportExportPrompts_OnClick")

        # 2. Get Help
        self.GetHelp = self.DialogModel.createInstance("com.sun.star.awt.UnoControlFixedHyperlinkModel")
        self.GetHelp.Name = "GetHelp"
        self.GetHelp.Enabled = True
        self.GetHelp.PositionX = dialogLeftPadding
        self.GetHelp.PositionY = self.ImportExportPrompts.PositionY + 16
        self.GetHelp.Width = 136
        self.GetHelp.Height = 10
        self.GetHelp.Label = "• Get Help"
        self.GetHelp.URL = "https://github.com/denniskhong/librethinker-extension"
        self.DialogModel.insertByName("GetHelp", self.GetHelp)

        # 3. Buy Mihail Marian A Coffee
        self.BuyMeCoffee = self.DialogModel.createInstance("com.sun.star.awt.UnoControlFixedHyperlinkModel")
        self.BuyMeCoffee.Name = "BuyMeCoffee"
        self.BuyMeCoffee.Enabled = True
        self.BuyMeCoffee.PositionX = dialogLeftPadding
        self.BuyMeCoffee.PositionY = self.GetHelp.PositionY + 12
        self.BuyMeCoffee.Width = 136
        self.BuyMeCoffee.Height = 10
        self.BuyMeCoffee.Label = "• Buy Mihail Marian A Coffee"
        self.BuyMeCoffee.URL = "https://ko-fi.com/mihailmarian"
        self.DialogModel.insertByName("BuyMeCoffee", self.BuyMeCoffee)

        # Push the settings header down to accommodate the vertical list
        self.SettingsSectionHeading = self.DialogModel.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
        self.SettingsSectionHeading.Name = "SettingsSectionHeading"
        self.SettingsSectionHeading.PositionX = dialogLeftPadding
        self.SettingsSectionHeading.PositionY = self.BuyMeCoffee.PositionY + 20
        self.SettingsSectionHeading.Width = 136
        self.SettingsSectionHeading.Height = 10
        self.SettingsSectionHeading.Label = "BYOK / Ollama Settings"
        self.DialogModel.insertByName("SettingsSectionHeading", self.SettingsSectionHeading)

        # --------- NEW: Button placed FIRST, right under the Settings Heading ---
        self.GetOllamaModels = self.DialogModel.createInstance(
            "com.sun.star.awt.UnoControlButtonModel"
        )
        self.GetOllamaModels.Name = "GetOllamaModels"
        self.GetOllamaModels.TabIndex = self.BuyMeCoffee.TabIndex + 1
        self.GetOllamaModels.PositionX = dialogLeftPadding
        self.GetOllamaModels.PositionY = self.SettingsSectionHeading.PositionY + 15
        self.GetOllamaModels.Width = 100
        self.GetOllamaModels.Height = BUTTON_HEIGHT
        self.GetOllamaModels.BackgroundColor = COLOR_BUTTON_SETTINGS
        self.GetOllamaModels.Label = "Get Ollama Models"

        self.DialogModel.insertByName("GetOllamaModels", self.GetOllamaModels)

        self.DialogContainer.getControl("GetOllamaModels").addActionListener(self)
        self.DialogContainer.getControl("GetOllamaModels").setActionCommand(
            "GetOllamaModels_OnClick"
        )

        # --------- CHANGE: ModelIdLabel anchored to the new button ---
        self.ModelIdLabel = self.DialogModel.createInstance(
            "com.sun.star.awt.UnoControlFixedTextModel"
        )
        self.ModelIdLabel.Name = "ModelIdLabel"
        self.ModelIdLabel.PositionX = dialogLeftPadding
        self.ModelIdLabel.PositionY = self.GetOllamaModels.PositionY + 30
        self.ModelIdLabel.Width = 136
        self.ModelIdLabel.Height = 10
        self.ModelIdLabel.Label = "Model ID (e.g. claude-opus-4-6)"
        self.ModelIdLabel.MultiLine = True

        self.DialogModel.insertByName("ModelIdLabel", self.ModelIdLabel)

        # --------- CHANGE: ComboBox placed below the Label ---
        self.ModelId = self.DialogModel.createInstance(
            "com.sun.star.awt.UnoControlComboBoxModel"
        )
        self.ModelId.Dropdown = True # Enables the dropdown arrow

        self.ModelId.Name = "ModelId"
        self.ModelId.TabIndex = self.GetOllamaModels.TabIndex + 1
        self.ModelId.PositionX = dialogLeftPadding
        self.ModelId.PositionY = self.ModelIdLabel.PositionY + 10
        self.ModelId.Width = 136
        self.ModelId.Height = 15
        self.ModelId.Text = self.settings.modelId

        self.DialogModel.insertByName("ModelId", self.ModelId)

        # --------- CHANGE: ModelUrlLabel anchored to the ComboBox ---
        self.ModelUrlLabel = self.DialogModel.createInstance(
            "com.sun.star.awt.UnoControlFixedTextModel"
        )
        self.ModelUrlLabel.Name = "ModelUrlLabel"
        self.ModelUrlLabel.PositionX = dialogLeftPadding
        self.ModelUrlLabel.PositionY = self.ModelId.PositionY + 20
        self.ModelUrlLabel.Width = 136
        self.ModelUrlLabel.Height = 10
        self.ModelUrlLabel.Label = "Model URL"

        self.DialogModel.insertByName("ModelUrlLabel", self.ModelUrlLabel)

        self.ModelUrl = self.DialogModel.createInstance(
            "com.sun.star.awt.UnoControlEditModel"
        )

        self.ModelUrl.Name = "ModelUrl"
        self.ModelUrl.TabIndex = self.ModelId.TabIndex + 1
        self.ModelUrl.PositionX = dialogLeftPadding
        self.ModelUrl.PositionY = self.ModelUrlLabel.PositionY + 10
        self.ModelUrl.Width = 136
        self.ModelUrl.Height = 15
        self.ModelUrl.Text = self.settings.modelUrl

        self.DialogModel.insertByName("ModelUrl", self.ModelUrl)

        self.ModelApiKeyLabel = self.DialogModel.createInstance(
            "com.sun.star.awt.UnoControlFixedTextModel"
        )
        self.ModelApiKeyLabel.Name = "ModelApiKeyLabel"
        self.ModelApiKeyLabel.PositionX = dialogLeftPadding
        self.ModelApiKeyLabel.PositionY = self.ModelUrl.PositionY + 20
        self.ModelApiKeyLabel.Width = 136
        self.ModelApiKeyLabel.Height = 10
        self.ModelApiKeyLabel.Label = "Model API key"
        self.ModelApiKeyLabel.MultiLine = True

        self.DialogModel.insertByName("ModelApiKeyLabel", self.ModelApiKeyLabel)

        self.ModelApiKey = self.DialogModel.createInstance(
            "com.sun.star.awt.UnoControlEditModel"
        )

        self.ModelApiKey.Name = "ModelApiKey"
        self.ModelApiKey.TabIndex = self.ModelId.TabIndex + 1
        self.ModelApiKey.PositionX = dialogLeftPadding
        self.ModelApiKey.PositionY = self.ModelApiKeyLabel.PositionY + 10
        self.ModelApiKey.Width = 136
        self.ModelApiKey.Height = 15
        self.ModelApiKey.Text = self.settings.apiKey
        self.ModelApiKey.EchoChar = 42

        # inserts the control model into the dialog model
        self.DialogModel.insertByName("ModelApiKey", self.ModelApiKey)
        
        # --------- NEW: Dropdown for Model Output In ---------
        self.ModelOutputInLabel = self.DialogModel.createInstance(
            "com.sun.star.awt.UnoControlFixedTextModel"
        )
        self.ModelOutputInLabel.Name = "ModelOutputInLabel"
        self.ModelOutputInLabel.PositionX = dialogLeftPadding
        self.ModelOutputInLabel.PositionY = self.ModelApiKey.PositionY + 20
        self.ModelOutputInLabel.Width = 136
        self.ModelOutputInLabel.Height = 10
        self.ModelOutputInLabel.Label = "Output Destination:"

        self.DialogModel.insertByName("ModelOutputInLabel", self.ModelOutputInLabel)

        self.ModelOutputIn = self.DialogModel.createInstance(
            "com.sun.star.awt.UnoControlComboBoxModel"
        )
        self.ModelOutputIn.Dropdown = True
        self.ModelOutputIn.Name = "ModelOutputIn"
        self.ModelOutputIn.TabIndex = self.ModelApiKey.TabIndex + 1
        self.ModelOutputIn.PositionX = dialogLeftPadding
        self.ModelOutputIn.PositionY = self.ModelOutputInLabel.PositionY + 10
        self.ModelOutputIn.Width = 136
        self.ModelOutputIn.Height = 15
        self.ModelOutputIn.StringItemList = ("Replace selected text", "Insert after selected text", "Model output box")
        self.ModelOutputIn.Text = "Model output box" # The default option

        self.DialogModel.insertByName("ModelOutputIn", self.ModelOutputIn)

        # --------- create an instance of Button control, set properties ---
        self.SaveSettings = self.DialogModel.createInstance(
            "com.sun.star.awt.UnoControlButtonModel"
        )
        self.SaveSettings.Name = "SaveSettings"
        self.SaveSettings.TabIndex = self.ModelOutputIn.TabIndex + 1
        self.SaveSettings.PositionX = dialogLeftPadding
        self.SaveSettings.PositionY = self.ModelOutputIn.PositionY + 25 # Anchored to the new dropdown
        self.SaveSettings.Width = 64
        self.SaveSettings.Height = BUTTON_HEIGHT
        self.SaveSettings.BackgroundColor = COLOR_BUTTON_SAVE
        self.SaveSettings.Label = "Save Settings"

        # inserts the control model into the dialog model
        self.DialogModel.insertByName("SaveSettings", self.SaveSettings)

        # add the action listener
        self.DialogContainer.getControl("SaveSettings").addActionListener(self)
        self.DialogContainer.getControl("SaveSettings").setActionCommand(
            "SaveSettings_OnClick"
        )

        self.SaveSettingsStatus = self.DialogModel.createInstance(
            "com.sun.star.awt.UnoControlFixedTextModel"
        )
        self.SaveSettingsStatus.Name = "SaveSettingsStatus"
        self.SaveSettingsStatus.PositionX = dialogLeftPadding
        self.SaveSettingsStatus.PositionY = self.SaveSettings.PositionY + 30 # Anchored to the button
        self.SaveSettingsStatus.Width = 136
        self.SaveSettingsStatus.Height = 30
        self.SaveSettingsStatus.Label = ""
        self.SaveSettingsStatus.MultiLine = True

        self.DialogModel.insertByName("SaveSettingsStatus", self.SaveSettingsStatus)

        # add the window listener
        self.DialogContainer.addWindowListener(self)

    # -----------------------------------------------------------
    #               Action events
    # -----------------------------------------------------------

    def actionPerformed(self, oActionEvent):

        if oActionEvent.ActionCommand == "Submit_OnClick":
            self.Submit_OnClick()

        if oActionEvent.ActionCommand == "SavePrompt_OnClick":
            self.SavePrompt_OnClick()

        if oActionEvent.ActionCommand == "SaveSettings_OnClick":
            self.SaveSettings_OnClick()

        if oActionEvent.ActionCommand == "GetOllamaModels_OnClick":
            self.GetOllamaModels_OnClick()

        if oActionEvent.ActionCommand == "NewPrompt_OnClick":
            self.NewPrompt_OnClick()

        if oActionEvent.ActionCommand == "DeletePrompt_OnClick":
            self.DeletePrompt_OnClick()

        if oActionEvent.ActionCommand == "ImportExportPrompts_OnClick":
            self.ImportExportPrompts_OnClick()

    def focusGained(self, event):
        control = event.Source
        control_name = control.Model.Name

        if control_name == "Prompt":
            if control.getText() == PROMPT_PLACEHOLDER:
                control.setText("")

        elif control_name == "PromptNameCombo":
            if control.getText() == PROMPT_NAME_PLACEHOLDER:
                control.setText("")

    def focusLost(self, event):
        control = event.Source
        control_name = control.Model.Name

        if control_name == "Prompt":
            if control.getText().strip() == "":
                control.setText(PROMPT_PLACEHOLDER)

        elif control_name == "PromptNameCombo":
            if control.getText().strip() == "":
                control.setText(PROMPT_NAME_PLACEHOLDER)

    # -----------------------------------------------------------
    #               Window (dialog/panel) events
    # -----------------------------------------------------------

    def windowResized(self, oWindowEvent):
        # print(dir(oWindowEvent.Source))
        self.resizeControls(dialog=oWindowEvent.Source)

    def disposing(self, event):
        pass

    def windowMoved(self, event):
        pass

    def windowShown(self, event):
        pass

    def windowHidden(self, event):
        pass


# ----------------- END GENERATED CODE ----------------------------------------
