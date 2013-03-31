#!usr/bin/python
#coding:utf-8

###################################
##いままで作ったEvernoteの関数たち###
##                    2013/3/31更新
###################################

import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient
import evernote.edam.userstore.UserStore as UserStore
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.notestore.NoteStore as NoteStore
import evernote.edam.type.ttypes as Types
import datetime

account = "sapicja"
authToken ="SECRET"

class Evernote():
    def __init__(self,authToken):
        evernoteHost = "www.evernote.com"
        userStoreUri = "https://" + evernoteHost + "/edam/user"
        userStoreHttpClient = THttpClient.THttpClient(userStoreUri)
        userStoreProtocol = TBinaryProtocol.TBinaryProtocol(userStoreHttpClient)
        userStore = UserStore.Client(userStoreProtocol)
        noteStoreUrl = userStore.getNoteStoreUrl(authToken)
        noteStoreHttpClient = THttpClient.THttpClient(noteStoreUrl)
        noteStoreProtocol = TBinaryProtocol.TBinaryProtocol(noteStoreHttpClient)
        self.noteStore = NoteStore.Client(noteStoreProtocol)
        d = datetime.datetime.today()
        self.today ="%s年%s月%s日" %(d.year,d.month,d.day)

    def GetNotebookGuid(self):#ノートブックのGuidを取得して表示
        Notebooks = self.noteStore.listNotebooks(authToken)
        for notebook in Notebooks:
            print notebook.name+" "+notebook.guid

    def FindNote(self,Words):
        def filter(): ##検索フィルターの設定  綺麗にかけないか
            filter = NoteStore.NoteFilter()
            filter.words = Words
            return filter
        def resultSpec(): ##検索結果の出力設定
            resultSpec = NoteStore.NotesMetadataResultSpec()
            resultSpec.includeTitle = True
            resultSpec.includeCreated = True
            resultSpec.includeUpdated = True
            resultSpec.includeAttributes = True
            return resultSpec
        # findNotesMetadata(authToken、フィルター、、取得するノート数)
        noteMetaList = self.noteStore.findNotesMetadata(authToken,filter(),0,30,resultSpec())
        return noteMetaList

    def MargeNotes(self,noteMetaList,MargedTitle,Taglist,NotebookGuid): ##ノートリスト内にあるノートをマージ
        def Content():
            noteContent = '<?xml version="1.0" encoding="UTF-8"?> \
                <!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd"><en-note>'
            for note in noteMetaList.notes:
                note = self.noteStore.getNote(authToken,note.guid,True,False,False,False)
                text = note.content[114:-10] ###最初の<?xml...の部分を消すために数えた.
                title = note.title
                noteContent += "<br>##########"+ title +"##########</br>"
                noteContent += text + "<br></br>"
#                self.noteStore.deleteNote(authToken,note.guid)
            noteContent += '</en-note>'
            return noteContent
        Title = MargedTitle
        MergeNote = Types.Note()
        MergeNote.notebookGuid = NotebookGuid
        MergeNote.title = Title
        MergeNote.content = Content()
        MergeNote.tagNames = Taglist
        self.noteStore.createNote(authToken,MergeNote)
        print "[OK] Marged note which Title is "+"["+Title+"]"



    def MakeDiaryNote(self):  ##日記ノートを作成
        note = Types.Note()
        d = datetime.datetime.today()
        date = datetime.datetime(2012,1,4)
        DiaryNumber = str((d-date).days+1)        
        today ="%s年%s月%s日" %(d.year,d.month,d.day)
        Title = "No." + DiaryNumber + ":" + today
        TagList = ["Diary",today]
        note.title = Title
        note.tagNames = TagList
        note.notebookGuid = "SECRET" ##DiaryノートブックのGUID
        createdNote = self.noteStore.createNote(authToken,note)
        print "Successfully created a new note with GUID:",createdNote.guid

    def TweetRandomNote(self):##ランダムにノートの内容を拾う
        notebookGuid="SECRET" 
         ##今やってるノートブックのGUID
        def filter(): ##検索フィルターの設定  クラスの継承とかべんきょうしたら
            filter = NoteStore.NoteFilter()
            filter.notebookGuid = notebookGuid
#            filter.words = "created:day-1 source:mail.smtp"
#            words = "created:day-"+str(day)+ " source:mail.smtp"
#            filter.words = words
            return filter
        def resultSpec(): ##検索結果の出力設定
            resultSpec = NoteStore.NotesMetadataResultSpec()
            resultSpec.includeTitle = True
            resultSpec.includeCreated = True
            resultSpec.includeUpdated = True
            resultSpec.includeAttributes = True
            return resultSpec
        ##ノートのリストを取得(一日に30通は来ないだろうということで)
        noteMetaList = self.noteStore.findNotesMetadata(authToken,filter(),0,30,resultSpec())
        print "TotalNotes: %s" % noteMetaList.totalNotes

        ran = random.random()
        num = int(ran*1000)% noteMetaList.totalNotes
        note = noteMetaList.notes[num]
        shareKey = self.noteStore.shareNote(authToken,note.guid)
        noteGuid = note.guid
        shareId = "SECRET" #自分で調べた
        shareURL = "http://www.evernote.com/shard/" + \
            shareId + "/sh/" + noteGuid + "/" + shareKey
        text = note.title+" : "+shareURL
#        print text
        return text
  
    def MakeNote(self,Title,Content,Tags):
        Note = Types.Note()
        Title = Title
        TagList = Tags
        Note.title = Title
        Note.tagNames = TagList
        NoteContent = '<?xml version="1.0" encoding="UTF-8"?> \
                <!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd"><en-note>'
        NoteContent += Content
        NoteContent += '</en-note>'
        Note.content = NoteContent
#        Note.notebookGuid = "SECRET" ##DiaryノートブックのGUID
        createdNote = self.noteStore.createNote(authToken,Note)
        print "Successfully created a new note with GUID:",createdNote.guid
        
            
def main():
    sapicja = Evernote(authToken)
#    sapicja.MakeNote("a")
#    sapicja.MergeNote()
#    sapicja.MakeDiaryNote()
#    sapicja.TweetRandomNote()
if __name__ == "__main__":
    main()
