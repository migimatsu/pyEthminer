
"""
CommandExecutor.py

    システムコマンドの実行クラス
"""

# インポート
import          select
from            signal              import      SIGSTOP, SIGCONT
from            subprocess          import      Popen, STDOUT, PIPE

# システムコマンドの実行クラス
class           CommandExecutor :
    """
    システムコマンドの実行クラス
    """

    # コマンドのプロセス情報
    proc : Popen or None        = None
    
    # コンストラクタ
    def             __init__( self, command : str, options : [ str ] = () ) -> None :
        """
        コンストラクタ

        :param command:        実行コマンド
        :param options:        オプション引数
        """

        # コマンドを起動する
        self.proc       = Popen( [ command, * options ], stdout = PIPE, stderr = STDOUT, )


    # コマンドから一行読み込み
    def             read( self, timeout : int or None = None ) -> str or None :
        """
        コマンドから読み込み

        :param timeout: 読み込みタイムアウト ms
        :return:        コマンドからの出力行を一行づつ返す。読めなければ None、EOF なら空文字列を返す
        """

        # 読めるかをチェックする
        r, _, _         = select.select( [ self.proc.stdout, ], [], [],
                                         None if not timeout else timeout / 1000.0, )

        # 読めなければ None を返す
        if not r :
            return None

        # 読めれば一行読む。EOF は空文字列が帰る
        else :
            return self.proc.stdout.readline().decode()


    # ジェネレータでコマンドから一行読み込み
    def             next( self, timeout : int or None = None ) -> [ str or None ] :
        """
        コマンドから読み込み

        :param timeout: 読み込みタイムアウト ms
        :return:        コマンドからの出力行を一行づつジェネレータで返す。読めなければ None、EOF なら終端を返す
        """

        # 標準出力または標準エラー出力を待ち、読めたらそれを一行返す。EOF なら終端を返す
        while True :

            # 読めるかをチェックする
            r, _, _         = select.select( [ self.proc.stdout, ], [], [],
                                             None if not timeout else timeout / 1000.0, )

            # 読めなければ None を返すのみ
            if not r :
                yield None

            # 読めれば一行読む
            else :
                l               = self.proc.stdout.readline().decode()

                # 読めた行を返す
                if l :
                    yield l

                # EOF (空文字列) なら終端
                else :
                    break


    # マイニングコマンド一時停止
    def             pause( self, ) -> None :
        """
        コマンド一時停止
        """
        
        if self.proc :
            self.proc.send_signal( SIGSTOP )

    # マイニングコマンド再開
    def             resume( self, ) -> None :
        """
        コマンド再開
        """

        if self.proc :
            self.proc.send_signal( SIGCONT )

    # マイニングコマンド終了
    def             terminate( self, timeout : int or None = None ) -> None :
        """
        コマンド終了
        
        :param timeout:         終了待ちタイムアウト
        """
        
        # コマンドがなければ何もしない
        if not self.proc :
            return
            
        # SIGTERM で終了させる
        self.proc.terminate()
        
        # 終了を待つ - timeout で終わらなければ強制終了する
        try :
            self.proc.wait( timeout / 1000.0 if timeout else None )
            
        # タイムアウト - SIGKILL で強制終了する
        except :
            self.proc.kill()
            self.proc.wait()
