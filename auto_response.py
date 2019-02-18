import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QSystemTrayIcon
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QMenu, QAction
from PyQt5.QtGui import QIcon

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
    def __init__(self):
        super().__init__()
        self.btn1 = QPushButton('点击创建二维码')
        self.btn2 = QPushButton('最小化到托盘')

        vbox = QVBoxLayout()
        vbox.addWidget(self.btn1)
        vbox.addWidget(self.btn2)

        main_widget = QWidget()
        main_widget.setLayout(vbox)
        self.setCentralWidget(main_widget)

        self.btn1.clicked.connect(self.respond)
        self.btn2.clicked.connect(self.toTray)

    def respond(self):

        itchat.auto_login()
        itchat.send("---Starting auto_repond-----\n{:}".format(time.ctime()),
                    toUserName='filehelper')
        itchat.run()

    def toTray(self):
        self.hide()
        self.setupTray()

    def setupTray(self):
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon('./data/chat.png'))

        self.tray_menu = QMenu(QApplication.desktop())
        self.RestoreAction = QAction('Restore', self, triggered=self.show)
        self.QuitAction = QAction('Exit', self, triggered=sys.exit)

        self.tray_menu.addAction(self.RestoreAction)
        self.tray_menu.addAction(self.QuitAction)
        self.tray.setContextMenu(self.tray_menu)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = Mainwindow()
    mainwindow.show()
    sys.exit(app.exec_())