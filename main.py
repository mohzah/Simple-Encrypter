# -*- coding: utf-8 -*-

"""Copyright Mohammad Hassan Zahraee 2016
"""

import os
import sys
import tarfile
import tempfile
from enum import Enum
from os.path import split
from mycipher import MyCipher
# Import Qt modules
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QDialogButtonBox

# Import the compiled UI module
# these modules are auto generated from .ui files designed in Qt Designer
from window_ui import Ui_MainWindow
from password_ui import Ui_PassDialog


BOXTYPE = Enum('BoxType', 'SUCCESS ERROR')


# Create a class for our main window
class Main(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # This is always the same
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def add_file(self):
        """Add files or directories to the list of files/directories"""
        file_dialog = QFileDialog(self)
        if file_dialog.exec_():
            filenames = file_dialog.selectedFiles()
            self.ui.listWidget.addItems(filenames)
            self.ui.encryptButton.setEnabled(True)

    def remove_file(self):
        """Removes selected files (addresses) from the list"""
        listWidget = self.ui.listWidget
        selected = listWidget.selectedItems()
        for item in selected:
            row = listWidget.row(item)
            listWidget.takeItem(row)
            del item
        if listWidget.count() == 0:
            # if list is empty, remove and encrypt buttons disabled
            self.ui.removeButton.setEnabled(False)
            self.ui.encryptButton.setEnabled(False)

    def selection_changed(self):
        """ Triggered when there is a change in selection in the list
            Item selected/deselected in the list.
        """
        listWidget = self.ui.listWidget
        if listWidget.count() > 0:
            self.ui.removeButton.setEnabled(True)
        else:
            self.ui.removeButton.setEnabled(False)

    def encrypt(self):
        """Implementation of UI's "Encrypt" button function"""
        listWidget = self.ui.listWidget
        # open a dialog to choose/create file that will be our encrypted file
        filter = 'Encrypted (*.encrypted)'
        save_file = QFileDialog.getSaveFileName(self,
                                                'Save encrypted file',
                                                filter=filter)[0]
        tempfile = save_file + ".tmp"
        if save_file:
            # Making a tar archive from all files in the list and save tar as
            # chosen by user in file dialog
            with tarfile.open(tempfile, "w") as tar:
                for i in range(listWidget.count()):
                    item = listWidget.item(i).text()
                    tar.add(item, split(item)[1])
            # Getting password(key) for encryption
            pass_dialog = PasswordDlg(self)
            if pass_dialog.exec_():
                password = pass_dialog.password()
                cipher = MyCipher(str(password), save_file)
                if cipher.encrypt():
                    self.message_box("Successful Encryption!")
                    os.remove(tempfile)

    def browse(self):
        self.encrypted_file = QFileDialog.getOpenFileName()[0]
        self.ui.lineEdit.setText(self.encrypted_file)

    def text_changed(self):
        if self.ui.lineEdit.text():
            self.ui.decryptButton.setEnabled(True)
        else:
            self.ui.decryptButton.setEnabled(False)

    def decrypt(self):
        """Implementation of UI's "Decrypt" button function"""
        pass_dialog = PasswordDlg(self)
        infile = self.ui.lineEdit.text()
        if not os.path.isfile(infile):
            self.message_box("File not found!")
            return
        if pass_dialog.exec_():
            password = pass_dialog.password()
            cipher = MyCipher(password, infile)
            outfile = cipher.decrypt()
            if outfile:
                dir, fname = split(outfile)
                prefix = fname.rsplit('.tar', 1)[0]+' '
                outdir = tempfile.mkdtemp(prefix=prefix, dir=dir)
                with tarfile.open(outfile, 'r') as tar:
                    tar.extractall(outdir)
                os.remove(outfile)
                self.message_box("Successful Decryption!")

    def message_box(self, text, type=BOXTYPE.SUCCESS):
        msgBox = QMessageBox()
        msgBox.setText(text)
        if type == BOXTYPE.SUCCESS:
            pixmap = QtGui.QPixmap(":/icon/image/check.png")
        elif type == BOXTYPE.ERROR:
            pixmap = QtGui.QPixmap(":/icon/image/delete.png")
        msgBox.setIconPixmap(pixmap)
        msgBox.exec_()


# create a class for our password dialog
class PasswordDlg(QDialog):
    """ Class Password Dialog
        implementation of password dialog
    """
    def __init__(self, parent=None, master=False):
        QDialog.__init__(self, parent=parent)

        # This is always the same
        self.ui = Ui_PassDialog()
        self.ui.setupUi(self)
        # setting icon for Ok button
        ok_button = self.ui.buttonBox.button(QDialogButtonBox.Ok)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/image/check.png"),
                       QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        ok_button.setIcon(icon)
        # adjust label if we are asking for master password
        if master:
            self.ui.label.setText("Enter Your Master Password:")
            self.setWindowTitle("Master Password")

    def password(self):
        return self.ui.lineEdit.text()

    def show_password(self):
        self.ui.lineEdit.setEchoMode(QLineEdit.Normal)


def main():
    # boilerplate code for Qt applications
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
