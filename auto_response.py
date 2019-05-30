import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QSystemTrayIcon
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QMenu, QAction, QLabel
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore

import itchat, re
from itchat.content import TEXT, PICTURE, MAP, CARD, NOTE, SHARING, RECORDING, ATTACHMENT, VIDEO

import time


# TODO: 群聊@自动回复
# TODO: multi_thread
# TODO: 最小化

REPLY = {'default': ''}

REMARK_TEMPLATE = '''
        Friend: {friend_nickname} 
        Time: {msg_time} 
        Message: {msg_content}
        '''

KEYS = ['年','快乐','猪']



@itchat.msg_register([TEXT, PICTURE, MAP, CARD, NOTE, SHARING, RECORDING, ATTACHMENT, VIDEO])



def text_reply(msg):

    friend = itchat.search_friends(userName=msg['FromUserName'])

    if msg['Type'] == 'Text':
        remark_content = REMARK_TEMPLATE.format(friend_nickname=friend['NickName'],
                                                msg_time=time.ctime(),
                                                msg_content=msg['Text'])
        itchat.send(remark_content, toUserName='filehelper')
        for key in KEYS:
            match = re.search(key, msg['Text'])

            if match:

                itchat.send(r"谢谢{user_name}，新年快乐~".format(user_name=friend['RemarkName']),
                             toUserName=msg['FromUserName'])
                break

        else:
            itchat.send(r"您好，我现在不方便，稍后回复您。",
                        toUserName=msg['FromUserName'])

    else:
        remark_content = REMARK_TEMPLATE.format(friend_nickname=msg['FromUserName'],
                                                msg_time=time.ctime(),
                                                msg_content=msg['Type'])
        itchat.send(remark_content, toUserName='filehelper')
        itchat.send(r"您好，我现在不方便，稍后回复您。",
                    toUserName=msg['FromUserName'])


class Mainwindow(QMainWindow):
    StartRespondSignal = QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()

        # <editor-fold desc="0.界面">
        self.btn1 = QPushButton('点击创建二维码')
        self.btn2 = QPushButton('最小化到托盘')
        self.lbl_status = QLabel('未登录')

        vbox = QVBoxLayout()
        vbox.addWidget(self.btn1)
        vbox.addWidget(self.btn2)
        vbox.addWidget(self.lbl_status)

        main_widget = QWidget()
        main_widget.setLayout(vbox)
        self.setCentralWidget(main_widget)

        self.setWindowIcon(QIcon('./data/icon.ico'))
        self.setupTray()
        # </editor-fold>

        # <editor-fold desc="1.connection">
        self.btn1.clicked.connect(self.start_subthread)
        self.btn2.clicked.connect(self.toTray)
        self.init_thread()
        # </editor-fold>

    def init_thread(self):
        self.sub_thread = QtCore.QThread()
        self.sub_thread_object = SubThreadObject()
        self.sub_thread_object.moveToThread(self.sub_thread)
        self.StartRespondSignal.connect(self.sub_thread_object.respond)
        self.sub_thread_object.LogStatus.connect(self.get_status)
        self.sub_thread.start()

    def start_subthread(self):
        self.StartRespondSignal.emit()

    def get_status(self, status):
        self.lbl_status.setText(status)

    def toTray(self):
        self.hide()
        self.tray.isVisible()

    def setupTray(self):
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon('./data/icon.ico'))

        self.tray_menu = QMenu(QApplication.desktop())  # 创建菜单
        self.RestoreAction = QAction('Restore', self, triggered=self.show)
        self.QuitAction = QAction('Exit', self, triggered=sys.exit)
        self.tray_menu.addAction(self.QuitAction)
        self.tray_menu.addAction(self.RestoreAction)  # 为菜单添加动作
        self.tray.setContextMenu(self.tray_menu)  #
        self.tray.show()


class SubThreadObject(QtCore.QObject):
    LogStatus = QtCore.pyqtSignal(str)
    def __init__(self):
        super(SubThreadObject, self).__init__()

    def respond(self):
        itchat.auto_login()
        self.LogStatus.emit('成功登录')
        itchat.send("---Starting auto_repond-----\n{:}".format(time.ctime()),
                    toUserName='filehelper')
        itchat.run()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = Mainwindow()
    mainwindow.show()
    sys.exit(app.exec_())