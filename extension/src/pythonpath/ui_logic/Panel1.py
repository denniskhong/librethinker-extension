# -*- coding: utf-8 -*-
#!/usr/bin/env python

# =============================================================================
#
# Write your code here
#
# =============================================================================

import uno, tempfile, unohelper
import os, random, string, threading
from .utils import is_older, is_self_hosted, self_hosted_model
from dataclasses import dataclass


from .settings import Settings
import traceback

from .api import LtClient, OllamaClient
from com.sun.star.awt.PosSize import POSSIZE
from com.sun.star.awt.MessageBoxButtons import (
    BUTTONS_OK,
    BUTTONS_OK_CANCEL,
    BUTTONS_YES_NO,
    BUTTONS_YES_NO_CANCEL,
    BUTTONS_RETRY_CANCEL,
    BUTTONS_ABORT_IGNORE_RETRY,
)
from com.sun.star.awt.MessageBoxButtons import (
    DEFAULT_BUTTON_OK,
    DEFAULT_BUTTON_CANCEL,
    DEFAULT_BUTTON_RETRY,
    DEFAULT_BUTTON_YES,
    DEFAULT_BUTTON_NO,
    DEFAULT_BUTTON_IGNORE,
)
from com.sun.star.awt.MessageBoxType import (
    MESSAGEBOX,
    INFOBOX,
    WARNINGBOX,
    ERRORBOX,
    QUERYBOX,
)
from com.sun.star.beans import PropertyValue

try:
    from ui.Panel1_UI import Panel1_UI, PROMPT_PLACEHOLDER, PROMPT_NAME_PLACEHOLDER
except ImportError:
    from pythonpath.ui.Panel1_UI import Panel1_UI, PROMPT_PLACEHOLDER, PROMPT_NAME_PLACEHOLDER

from .prompt_manager import PromptManager

from com.sun.star.awt import XActionListener

class WorkflowDialogListener(unohelper.Base, XActionListener):
    """Listens to button clicks inside the Import/Export dialog."""
    def __init__(self, parent_panel, dialog):
        self.parent = parent_panel
        self.dialog = dialog

    def actionPerformed(self, event):
        cmd = event.ActionCommand
        if cmd == "Import":
            self.parent._execute_import()
            self.dialog.endExecute()
        elif cmd == "Export":
            self.parent._execute_export()
            self.dialog.endExecute()
        elif cmd == "Guide":
            self.parent._show_format_guide()
        elif cmd == "Cancel":
            self.dialog.endExecute()

# -------------------------------------
# HELPERS FOR MRI AND  XRAY
# -------------------------------------

# Uncomment for MRI
# def mri(ctx, target):
#     mri = ctx.ServiceManager.createInstanceWithContext("mytools.Mri", ctx)
#     mri.inspect(target)

# Uncomment for Xray
# def xray(myObject):
#     try:
#         sm = uno.getComponentContext().ServiceManager
#         mspf = sm.createInstanceWithContext("com.sun.star.script.provider.MasterScriptProviderFactory", uno.getComponentContext())
#         scriptPro = mspf.createScriptProvider("")
#         xScript = scriptPro.getScript("vnd.sun.star.script:XrayTool._Main.Xray?language=Basic&location=application")
#         xScript.invoke((myObject,), (), ())
#         return
#     except:
#         raise _rtex("\nBasic library Xray is not installed", uno.getComponentContext())
# -------------------------------------------------------------------


@dataclass
class Response:
    answer: str
    label: str


class Panel1(Panel1_UI):
    """
    Class documentation...
    """

    def __init__(
        self, ctx=uno.getComponentContext(), dialog=None, **kwargs
    ):  # (self, panelWin, context=uno.getComponentContext()):

        try:
            self.ctx = ctx
            self.dialog = dialog

            self.settings = Settings(ctx)
            self.prompt_manager = PromptManager(ctx)
            Panel1_UI.__init__(
                self, ctx=self.ctx, dialog=self.dialog, settings=self.settings
            )
            self._refresh_prompt_dropdown()

        except Exception as e:
            self.messageBox(
                f"Error initializing panel: {str(traceback.format_exc())}",
                "Error",
                ERRORBOX,
            )

    def getHeight(self):
        return self.DialogContainer.Size.Height

    # --------- my code ---------------------
    # mri(self.LocalContext, self.DialogContainer)
    # xray(self.DialogContainer)

    def myFunction(self):
        # TODO: not implemented
        pass

    # --------- helpers ---------------------

    def messageBox(self, MsgText, MsgTitle, MsgType=MESSAGEBOX, MsgButtons=BUTTONS_OK):
        sm = self.ctx.ServiceManager
        si = sm.createInstanceWithContext("com.sun.star.awt.Toolkit", self.ctx)
        mBox = si.createMessageBox(self.Toolkit, MsgType, MsgButtons, MsgTitle, MsgText)
        mBox.execute()

    def showPanel(self):
        """
        Show the UI when it is embedded in the LibreOffice sidebar.

        Do not call execute() here, because the sidebar panel is already
        hosted by LibreOffice. execute() is only for standalone dialogs.
        """
        self.DialogContainer.setVisible(True)


    # -----------------------------------------------------------
    #               Execute dialog
    # -----------------------------------------------------------

    def showDialog(self):
        self.DialogContainer.setVisible(True)
        self.DialogContainer.createPeer(self.Toolkit, None)
        self.DialogContainer.execute()

    # -----------------------------------------------------------
    #               Action events
    # -----------------------------------------------------------

    def get_all_txt(self):
        desktop = self.ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.frame.Desktop", self.ctx
        )
        document = desktop.getCurrentComponent()

        tmp_dir = tempfile.gettempdir()
        name = (
            "".join(random.choices(string.ascii_lowercase + string.digits, k=12))
            + ".txt"
        )
        out_path = os.path.join(tmp_dir, name)

        file_url = unohelper.systemPathToFileUrl(os.path.abspath(out_path))

        props = (
            PropertyValue(Name="FilterName", Value="Text (encoded)"),
            PropertyValue(
                Name="FilterData", Value=(PropertyValue(Name="Encoding", Value="UTF8"),)
            ),
        )

        document.storeToURL(file_url, props)

        with open(out_path, "r", encoding="utf-8-sig", errors="replace") as f:
            txt = f.read()

        try:
            os.remove(out_path)
        except OSError:
            pass

        return txt

    def get_selected_txt(self):
        desktop = self.ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.frame.Desktop", self.ctx
        )
        model = desktop.getCurrentComponent()
        selection = model.CurrentController.getSelection()
        text_range = selection.getByIndex(0)
        return text_range.getString()

    def Submit_OnClick(self):
        try:
            if self.Submit.Enabled is False:
                return

            # Grab the live UI control for the Selected Text option
            selected_text_ctrl = self.DialogContainer.getControl("SelectedTextOption")
            
            # Explicitly check if the State integer equals 1 (checked)
            if selected_text_ctrl.State == 1:
                docText = self.get_selected_txt()
                # Check if the selection text is actually empty (nothing was highlighted)
                if not docText or docText.strip() == "":
                    self.messageBox(
                        "No text is currently selected. Please highlight some text in your document first, or choose 'Entire Document'.", 
                        "Selection Empty", 
                        WARNINGBOX
                    )
                    self.Submit.Enabled = True
                    self.StatusText.Label = ""
                    return
            else:
                # If Selected Text is NOT checked, default to grabbing the entire document
                docText = self.get_all_txt()

            self.Submit.Enabled = False
            self.StatusText.Label = "Loading..."
            
            # --------- NEW: Clear output box on new submit ---------
            output_box = self.DialogContainer.getControl("ModelOutputBox")
            if output_box:
                output_box.setText("")

            threading.Thread(target=self.submit_background, args=(docText,)).start()

        except Exception as e:
            self.messageBox(str(e), "Error", ERRORBOX)
            self.Submit.Enabled = True
            self.StatusText.Label = ""

    def submit_background(self, docText: str):
        try:
            inputPrompt: str = self.DialogContainer.getControl("Prompt").getText()

            if self.settings.savedPrompt and inputPrompt != self.settings.savedPrompt:
                self.settings.clearPrompt()

            model: str = self.DialogContainer.getControl("ModelId").getText()
            modelUrl: str = self.DialogContainer.getControl("ModelUrl").getText()
            apiKey: str = self.DialogContainer.getControl("ModelApiKey").getText()

            response = (
                self.server_response(inputPrompt, docText, model, apiKey)
                if not is_self_hosted(model)
                else self.ollama_response(
                    inputPrompt, docText, self_hosted_model(model), modelUrl, apiKey
                )
            )

            desktop = self.ctx.ServiceManager.createInstanceWithContext(
                "com.sun.star.frame.Desktop", self.ctx
            )
            currentComponent = desktop.getCurrentComponent()
            selection = currentComponent.CurrentController.getSelection()
            text_range = selection.getByIndex(0)
            
            desktop = self.ctx.ServiceManager.createInstanceWithContext(
                "com.sun.star.frame.Desktop", self.ctx
            )
            currentComponent = desktop.getCurrentComponent()
            selection = currentComponent.CurrentController.getSelection()
            text_range = selection.getByIndex(0)
            
            # --------- CHANGE: Route output based on dropdown selection ---------
            output_display_mode = self.DialogContainer.getControl("ModelOutputIn").getText()
            
            if output_display_mode == "Model output box":
                # Send the text directly to the new UI box, leave the document alone
                self.DialogContainer.getControl("ModelOutputBox").setText(response.answer)
                
            elif output_display_mode == "Insert after selected text":
                doc_text = text_range.getText()
                cursor = doc_text.createTextCursorByRange(text_range)
                cursor.collapseToEnd()
                doc_text.insertString(cursor, " " + response.answer, True)
                cursor.CharColor = 0xFF0000
                cursor.collapseToEnd()
                
            else: 
                # "Replace selected text" (This acts as our default fallback)
                text_range.setString(response.answer)
            # --------------------------------------------------------------------

            self.StatusText.Label = response.label

        except Exception as e:
            self.messageBox(str(e), "Error", ERRORBOX)
            self.StatusText.Label = ""
        finally:
            self.Submit.Enabled = True

    def server_response(
        self, inputPrompt: str, docText: str, model: str, apiKey: str
    ) -> Response:
        extensionVersion = "0.2.16-dk.4"

        client = LtClient(extensionVersion=extensionVersion)
        answer = client.getAnswer(
            inputPrompt=inputPrompt, docText=docText, apiKey=apiKey, model=model
        )

        freeModel = len(apiKey) == 0 and len(model) == 0

        if not answer.success:
            error_message = "Error getting response."
            if freeModel:
                error_message += "\nYou are using the free model which may have issues. Try again later or set up an API key."

            error_message += (
                f"\nRequest ID: {client.requestId}.\nDetails: {str(answer.message)}"
            )
            raise Exception(error_message)

        label = "Done."
        if is_older(extensionVersion, answer.latestExtensionVersion):
            label += " New version is out, please update."

        if freeModel:
            label += " You're using a free model; visit librethinker.com to learn about alternatives."
        else:
            label += f" Generated with model {model}."

        return Response(answer=answer.response, label=label)

    def ollama_response(
        self, userPrompt: str, text: str, model: str, modelUrl: str, apiKey: str
    ) -> Response:
        client = OllamaClient()
        answer = client.getAnswer(
            userPrompt=userPrompt,
            text=text,
            model=model,
            modelUrl=modelUrl,
            apiKey=apiKey,
        )
        if not answer.success:
            error_message = (
                f"Error getting response from Ollama.\nDetails: {str(answer.message)}"
            )
            raise Exception(error_message)
        label = f"Done. Generated with Ollama model {model}."
        return Response(answer=answer.response, label=label)

    def _refresh_prompt_dropdown(self):
        """Helper to refill the dropdown menu, sorted alphabetically."""
        dropdown = self.DialogContainer.getControl("PromptNameCombo")
        dropdown.removeItems(0, dropdown.getItemCount())
        prompts = self.prompt_manager.get_prompt_list()

        # Sort case-insensitive
        sorted_prompts = sorted(prompts, key=str.lower)
        if sorted_prompts:
            dropdown.addItems(tuple(sorted_prompts), 0)

    def itemStateChanged(self, oItemEvent):
        """Fires when a user selects a prompt from the dropdown or toggles a radio button."""
        control = oItemEvent.Source
        control_name = control.Model.Name
        
        # 1. Prompt Dropdown Logic
        if control_name == "PromptNameCombo":
            dropdown = self.DialogContainer.getControl("PromptNameCombo")
            selected_name = dropdown.getText()
            
            if selected_name in self.prompt_manager.prompts:
                self.DialogContainer.getControl("Prompt").setText(self.prompt_manager.prompts[selected_name])
                self.StatusText.Label = f"Loaded '{selected_name}'"
                
        # 2. Mutual Exclusivity Logic for Radio Buttons
        elif control_name == "SelectedText":
            if control.Model.State == 1:
                self.DialogContainer.getControl("EntireDocumentOption").Model.State = 0
                
        elif control_name == "EntireDocument":
            if control.Model.State == 1:
                self.DialogContainer.getControl("SelectedTextOption").Model.State = 0

    def NewPrompt_OnClick(self):
        """Clears the canvas for a new entry."""
        combo = self.DialogContainer.getControl("PromptNameCombo")
        combo.setText(PROMPT_NAME_PLACEHOLDER)
        
        self.DialogContainer.getControl("Prompt").setText(PROMPT_PLACEHOLDER)
        self.StatusText.Label = "Ready for a new prompt."
        
        # Push focus to the combo box so they can type immediately
        combo.setFocus()

    def DeletePrompt_OnClick(self):
        """Deletes the currently displayed prompt."""
        name = self.DialogContainer.getControl("PromptNameCombo").getText()
        if self.prompt_manager.delete_prompt(name):
            self.NewPrompt_OnClick() # Clear the canvas
            self._refresh_prompt_dropdown()
            self.StatusText.Label = "Prompt deleted."
        else:
            self.StatusText.Label = "Cannot delete: Prompt not found."

    def ImportExportPrompts_OnClick(self):
        """Builds and launches the secondary workflow dialog for Import/Export."""
        smgr = self.ctx.ServiceManager
        dialog_model = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialogModel", self.ctx)
        dialog_model.PositionX = 150
        dialog_model.PositionY = 150
        dialog_model.Width = 120
        dialog_model.Height = 85
        dialog_model.Title = "Import/Export Prompts"

        dialog = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialog", self.ctx)
        dialog.setModel(dialog_model)
        
        listener = WorkflowDialogListener(self, dialog)

        # Helper to create buttons
        def add_btn(name, label, y_pos, cmd):
            btn = dialog_model.createInstance("com.sun.star.awt.UnoControlButtonModel")
            btn.Name = name
            btn.PositionX = 10
            btn.PositionY = y_pos
            btn.Width = 100
            btn.Height = 14
            btn.Label = label
            dialog_model.insertByName(name, btn)
            control = dialog.getControl(name)
            control.addActionListener(listener)
            control.setActionCommand(cmd)

        add_btn("BtnImport", "Import Prompts...", 10, "Import")
        add_btn("BtnExport", "Export All Prompts...", 28, "Export")
        add_btn("BtnGuide", "Format Guide", 46, "Guide")
        add_btn("BtnCancel", "Cancel", 64, "Cancel")

        dialog.createPeer(self.Toolkit, None)
        dialog.execute()
        dialog.dispose()

    def _execute_import(self):
        try:
            file_picker = self.ctx.ServiceManager.createInstanceWithContext(
                "com.sun.star.ui.dialogs.FilePicker", self.ctx
            )
            file_picker.initialize((uno.getConstantByName("com.sun.star.ui.dialogs.TemplateDescription.FILEOPEN_SIMPLE"),))
            file_picker.appendFilter("Supported Formats (*.json, *.md, *.yaml)", "*.json;*.md;*.yaml;*.yml")

            if file_picker.execute() == 1:
                selected_files = file_picker.getFiles()
                if selected_files:
                    system_path = uno.fileUrlToSystemPath(selected_files[0])
                    imported, skipped = self.prompt_manager.import_prompts(system_path)
                    
                    self._refresh_prompt_dropdown()
                    self.messageBox(f"Import complete.\n\nAdded/Updated: {imported}\nExact duplicates skipped: {skipped}", "Import Complete", INFOBOX)
        except Exception as e:
            self.messageBox(f"Import failed: {str(e)}", "Error", ERRORBOX)

    def _execute_export(self):
        try:
            file_picker = self.ctx.ServiceManager.createInstanceWithContext(
                "com.sun.star.ui.dialogs.FilePicker", self.ctx
            )
            file_picker.initialize((uno.getConstantByName("com.sun.star.ui.dialogs.TemplateDescription.FILESAVE_SIMPLE"),))
            file_picker.appendFilter("JSON File (*.json)", "*.json")
            file_picker.appendFilter("Markdown File (*.md)", "*.md")
            file_picker.appendFilter("YAML File (*.yaml)", "*.yaml")
            file_picker.setDefaultName("librethinker_prompts.json")

            if file_picker.execute() == 1:
                selected_files = file_picker.getFiles()
                if selected_files:
                    system_path = uno.fileUrlToSystemPath(selected_files[0])
                    count = self.prompt_manager.export_prompts(system_path)
                    self.messageBox(f"Successfully exported {count} prompts.", "Export Complete", INFOBOX)
        except Exception as e:
            self.messageBox(f"Export failed: {str(e)}", "Error", ERRORBOX)

    def _show_format_guide(self):
        guide_text = (
            "Supported Import Formats:\n\n"
            "JSON (.json): Standard dictionary format.\n"
            "  {\"Name\": \"Prompt text...\"}\n\n"
            "Markdown (.md): Header followed by rule.\n"
            "  # Prompt Name\n"
            "  Prompt text...\n"
            "  ---\n\n"
            "YAML (.yaml): Key with block scalar.\n"
            "  \"Prompt Name\":\n"
            "    | \n"
            "      Prompt text..."
        )
        self.messageBox(guide_text, "Format Guide", INFOBOX)

    def SavePrompt_OnClick(self):
        """Saves or updates the prompt using the auto-naming fallback."""
        try:
            name = self.DialogContainer.getControl("PromptNameCombo").getText()
            prompt = self.DialogContainer.getControl("Prompt").getText()
            
            final_name = self.prompt_manager.save_prompt(name, prompt)
            
            # Update the UI to reflect the actual saved name (in case fallback was used)
            self._refresh_prompt_dropdown()
            self.DialogContainer.getControl("PromptNameCombo").setText(final_name)
            
            self.StatusText.Label = "Prompt saved."
        except Exception as e:
            self.messageBox(f"Error saving prompt: {str(e)}", "Error", ERRORBOX)

    def GetOllamaModels_OnClick(self):
        try:
            self.StatusText.Label = "Fetching models..."
            # Disable button to prevent spam clicking
            btn = self.DialogContainer.getControl("GetOllamaModels")
            if btn:
                btn.Enable = False
                
            threading.Thread(target=self.get_ollama_models_background).start()
        except Exception as e:
            self.messageBox(str(e), "Error", ERRORBOX)

    def get_ollama_models_background(self):
        try:
            modelUrl = self.DialogContainer.getControl("ModelUrl").getText()
            client = OllamaClient()
            
            # This triggers the fallback logic and error handling in api.py
            models = client.getModels(modelUrl)

            if not models:
                # Dialog box if connection succeeded but no models are found
                self.messageBox("No models found. Make sure you have pulled at least one model into Ollama.", "Info", INFOBOX)
                self.StatusText.Label = ""
                return
            
            # LibreThinker expects Ollama models to be prefixed with 'sh/ollama/'
            formatted_models = [f"sh/ollama/{m}" for m in models]
            
            model_combo = self.DialogContainer.getControl("ModelId")
            
            # Clear existing dropdown items and add the newly sorted ones
            model_combo.removeItems(0, model_combo.getItemCount())
            model_combo.addItems(tuple(formatted_models), 0)
            
            # Auto-select the first model if the current text is empty or invalid
            current_text = model_combo.getText()
            if current_text not in formatted_models:
                model_combo.setText(formatted_models[0])

            self.StatusText.Label = "Ollama models loaded."
            
        except Exception as e:
            # Pops up the dialog box with the exact error if Ollama isn't running
            self.messageBox(str(e), "Connection Error", ERRORBOX)
            self.StatusText.Label = ""
            
        finally:
            # Always re-enable the button when the task finishes or fails
            btn = self.DialogContainer.getControl("GetOllamaModels")
            if btn:
                btn.Enable = True

    def SaveSettings_OnClick(self):
        try:
            if self.SaveSettings.Enabled is False:
                return

            self.SaveSettingsStatus.Label = "Saving..."
            self.SaveSettings.Enabled = False

            model = self.DialogContainer.getControl("ModelId").getText()
            apiKey = self.DialogContainer.getControl("ModelApiKey").getText()
            modelUrl = self.DialogContainer.getControl("ModelUrl").getText()

            self.settings.save(modelId=model, apiKey=apiKey, modelUrl=modelUrl)

            self.SaveSettingsStatus.Label = "Saved."

        except Exception as e:
            self.messageBox(f"Error saving settings: {str(e)}", "Error", ERRORBOX)
            self.SaveSettingsStatus.Label = ""
        finally:
            self.SaveSettings.Enabled = True

    # -----------------------------------------------------------
    #               Window (dialog/panel) events
    # -----------------------------------------------------------

    def resizeControls(self, dialog):
        # # see https://forum.openoffice.org/en/forum/viewtopic.php?f=45&t=85181#
        # ratio = 1.1
        # margin = 5
        # dlg_width = dialog.Size.Width
        # # add control names
        # controls = ['btnOK', 'lbList', 'cbPrinters']
        # for c in controls:
        #    cntr = dialog.getControl(c)
        #    width = (dlg_width / ratio) - margin
        #    cntr.setPosSize(cntr.PosSize.X, cntr.PosSize.Y, width, cntr.PosSize.Height, POSSIZE)
        pass


def Run_Panel1(*args):
    """
    Intended to be used in a development environment only
    Copy this file in src dir and run with (Tools - Macros - MyMacros)
    After development copy this file back
    """
    try:
        ctx = remote_ctx  # IDE
    except:
        ctx = uno.getComponentContext()  # UI

    # dialog
    dialog = ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.awt.UnoControlDialog", ctx
    )

    app = Panel1(ctx=ctx, dialog=dialog)
    app.showDialog()


g_exportedScripts = (Run_Panel1,)

# -------------------------------------
# HELPER FOR AN IDE
# -------------------------------------


if __name__ == "__main__":
    """Connect to LibreOffice proccess.
    1) Start the office in shell with command:
    soffice "--accept=socket,host=127.0.0.1,port=2002,tcpNoDelay=1;urp;StarOffice.ComponentContext" --norestore
    2) Run script
    """
    import os
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), "pythonpath"))

    local_ctx = uno.getComponentContext()
    resolver = local_ctx.ServiceManager.createInstance(
        "com.sun.star.bridge.UnoUrlResolver"
    )
    try:
        remote_ctx = resolver.resolve(
            "uno:socket,"
            "host=127.0.0.1,"
            "port=2002,"
            "tcpNoDelay=1;"
            "urp;"
            "StarOffice.ComponentContext"
        )
    except Exception as err:
        print(err)

    Run_Panel1()
