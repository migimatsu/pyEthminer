
"""
Miner.py

        画面・イベントごとにアクションを行い、その結果を返す
"""

# インポート
import          threading
from            common.Log              import      Log
from            common.Props            import      Props
from            common.CommandExecutor  import      CommandExecutor

from            Layout                  import      GREEN, RED, YELLOW, BLUE


# マイニングコマンドの実行クラス
class           Miner :
    """
    マイニングコマンドの実行クラス
    """

    # コマンド実行インスタンス
    _miner : CommandExecutor or None    = None

    # コマンドとオプション引数
    _cmd : str                          = ''
    
    # オプション引数
    _opts : list[ str ]                 = []
    
    # 接続先プール
    _pool : str                         = ''
    
    # コマンド停止スレッド
    _stopper : threading.Thread or None = None

    # コンストラクタ
    def             __init__( self, ) :
        """
        コンストラクタ
        """

        # コマンド実行インスタンス
        _miner          = None

        # コマンド
        self._cmd       = Props.props( 'MINER', 'CMD' )
        
        # 接続先プール
        self._pool      = (
            Props.props( 'POOL', 'PROTOCOL' )
                + '://' + Props.props( 'POOL', 'USER' ) + '.' + Props.props( 'POOL', 'WORKER' )
                + '@' + Props.props( 'POOL', 'HOST' )
        )

        # オプション引数
        self._opts      = [ *Props.props( 'MINER', 'OPTIONS' ).split(), '-P', self._pool ]

        # 実行ステータス - Job / Accepted / Rejected の数と Solution のリスト
        self._status    = { 'job' : 0, 'accept' : 0, 'reject' : 0, 'sols' : [] }
        self._wait      = 0

        # コマンド停止スレッド
        self._stopper   = None
        
    #
    # コマンド制御
    #

    # マイニングコマンドの制御アクション処理
    def             do( self, screen : str, event : str, _ : dict ) -> dict[ str, str or dict ] or None :
        """
        マイニングコマンドの制御アクション処理

        イベントに対応するアクションを実行し、実行結果を更新データとして返す

        :param screen:      画面名
        :param event:       発生したイベント名
        :param _:           受信したフォームデータの組
        :return:            結果としてのフォーム更新データ（文字列またはフィールド名と値の組）。None なら終了を示す
        """
        
        # ロガー
        _               = Log( __name__ )

        # アクションの結果領域
        result          = {}

        # main・start - マイニングコマンドを開始する
        if screen == 'main' and event == 'start' :
            result          = self.start()

        # main・_ - 画面イベントタイムアウト
        elif screen == 'main' and event == '_' :
            result          = self.status()

            # タイムアウトループで停止待ちなら停止チェックをする
            if self._stopper :
                result          |= self.wait_stop()

        # main・pause - マイニングコマンドを一時停止する
        elif screen == 'main' and event == 'pause' :
            result          = self.pause()

        # main・resume - マイニングコマンドを再開する
        elif screen == 'main' and event == 'resume' :
            result          = self.resume()

        # main・stop - マイニングコマンドを停止する
        elif screen == 'main' and event == 'stop' :
            result          = self.stop()

        # main・close - ウィンドウを終了する
        elif ( screen == 'main' and event == 'close' ) or event is None :
            self.stop()
            return None
            
        # 対応するアクションがなければメッセージを出す
        else :
            result[ 'msg' ] = '!!! 画面 {} イベント {} が定義されていません'.format( screen, event )

        # 結果 (画面の更新データ) を返す - None を返すと window は終了する
        return result


    # マイニングコマンドの起動処理
    def             start( self, ) -> dict or None :
        """
        マイニングコマンドを起動し、実行結果を更新データとして返す

        :return:        実行結果の更新データ。None なら終了を示す
        """
    
        # 結果領域
        result              = {}
    
        # すでに起動していなる時はメッセージを出す
        if self._miner :
            result[ 'msg' ]     = '!!! コマンドはすでに起動しています'
            return result

        # コマンドを起動する
        self._miner         = CommandExecutor( self._cmd, self._opts )
    
        # 画面の更新データを設定する
        result[ 'start'  ]  = { 'disabled' : True  }
        result[ 'pause'  ]  = { 'disabled' : False }
        result[ 'resume' ]  = { 'disabled' : True  }
        result[ 'stop'   ]  = { 'disabled' : False }
    
        result[ 'rate'   ]  = { 'text' : '', 'background_color' : GREEN }

        result[ 'pool'   ]  = self._pool
        
        result[ 'msg'    ]  = 'マイニング中です...'

        # 更新データを返す
        return result


    # マイニングコマンドの一時停止処理
    def             pause( self, ) -> dict :
        """
        マイニングコマンドを一時停止する

        :return:        実行結果の更新データ
        """

        # 結果領域
        result              = {}
        
        # 起動していない時はメッセージを出す
        if not self.isAlive() :
            result[ 'msg' ]     = '!!! コマンドが起動していません'
            return result

        # コマンドを一時停止する
        self._miner.pause()

        # 画面の更新データを設定する
        result[ 'start'  ]  = { 'disabled' : True  }
        result[ 'pause'  ]  = { 'disabled' : True  }
        result[ 'resume' ]  = { 'disabled' : False }
        result[ 'stop'   ]  = { 'disabled' : False }
        
        result[ 'rate'   ]  = { 'text' : '', 'background_color' : YELLOW }

        result[ 'msg'    ]  = '一時停止しています...'
        
        return result


    # マイニングコマンドの一時停止処理
    def             resume( self, ) -> dict :
        """
        マイニングコマンドを一時停止する

        :return:        実行結果の更新データ
        """
    
        # 結果領域
        result              = {}

        # 起動していない時はメッセージを出す
        if not self.isAlive() :
            result[ 'msg' ]     = '!!! コマンドが起動していません'
            return result

        # コマンドを再開する
        self._miner.resume()
        
        result[ 'start'  ]  = { 'disabled' : True  }
        result[ 'pause'  ]  = { 'disabled' : False }
        result[ 'resume' ]  = { 'disabled' : True  }
        result[ 'stop'   ]  = { 'disabled' : False }
        
        result[ 'rate'   ]  = { 'text' : '', 'background_color' : GREEN }

        result[ 'msg'    ]  = 'マイニング中です...'
        
        return result


    # マイニングコマンドの停止処理
    def             stop( self, ) -> dict :
        """
        マイニングコマンドを別スレッドで停止する

        :return:        実行結果の更新データ
        """
    
        # 結果領域
        result              = {}

        # 起動していない時はメッセージを出す
        if not self.isAlive() :
            result[ 'msg' ]     = '!!! コマンドが起動していません'
            return result

        # コマンドを停止する - 停止まで時間がかかるので別スレッドとする
        self._stopper       = threading.Thread( target = lambda : self._miner.terminate( 108000 ) )
        self._stopper.start()

        # 画面の更新データを設定する
        result[ 'start'  ]  = { 'disabled' : True }
        result[ 'pause'  ]  = { 'disabled' : True }
        result[ 'resume' ]  = { 'disabled' : True }
        result[ 'stop'   ]  = { 'disabled' : True }
        
        result[ 'rate'   ]  = { 'text' : '', 'background_color' : RED }
        
        result[ 'pool'   ]  = ''

        result[ 'msg'    ]  = '停止しています...(しばらくお待ちください)'
        
        return result


    # マイニングコマンドの停止待ち処理
    def             wait_stop( self, ) -> dict :
        """
        マイニングコマンドを別スレッドで停止されるのを待つ

        :return:        実行結果の更新データ
        """
    
        # 結果領域
        result              = {}
        
        # 停止処理が終わったかをチェックする
        self._stopper.join( timeout = 100 / 1000.0 )
        
        # 終了したなら、停止スレッドとマイニングコマンドのインスタンスを消す
        if not self._stopper.is_alive() :
            self._miner         = None
            self._stopper       = None
            
            # 画面の更新データを設定する
            result[ 'start'  ]  = { 'disabled' : False }
            result[ 'pause'  ]  = { 'disabled' : True  }
            result[ 'resume' ]  = { 'disabled' : True  }
            result[ 'stop'   ]  = { 'disabled' : True  }

            result[ 'msg' ]     = ''

        return result


    # コマンド出力から画面を更新処理
    def             status( self, ) -> dict :
        """
        コマンドから出力が読めれば、読んでステータスを更新する

        :return:        実行結果の更新データ。None なら終了を示す
        """

        log                 = Log( __name__ )

        # 画面更新データ
        result              = {}

        # コマンド出力があるかをを読んでみる
        line                = self.read()
        
        # EOF の時はメッセージを出力する
        if line == '' :
            result[ 'msg' ]     = '!!! EOF を検出しました'
            return result

        # 空文字列の時は何もしない
        if line is None :
            return result

        # 行をログして単語に分解する
        line                = line.replace( '\n', '' )
        
        # DEBUG : タイムアウト/EOF 以外の入力をトレース
        log.info( line )
        
        col                 = line.split()

        # 文字がない時は何もしない
        if len( col ) == 0 :
            return result
    
        # 'cl' で始まる Solution 行の時 -  Solution のリストに更新する
        if col[ 0 ] == 'cl' and line.find( 'Sol:' ) > 0 :
            self._wait                  += 1
            result                      |= self._addSolution( col[ 1 ], col[ 6 ] )

        # 'i' で始まる Job 行の時 - Job 行を更新する
        elif col[ 0 ] == 'i' and line.find( 'Job:' ) > 0 :
            self._status[ 'job' ]       += 1
            result[ 'job' ]             = '{:010} : {} : {}'.format( self._status[ 'job' ], col[ 1 ], col[ 3 ], )
    
        # 'i' で始まる Accept 行の時 - Solution のリストを ACCEPT で更新する
        elif col[ 0 ] == 'i' and 'Accept' in line and self._wait :
        
            # Accept 数を更新する　
            self._status[ 'accept' ]    += 1
            self._wait                  -= 1
            result[ 'accept' ]          = '{:010}'.format( self._status[ 'accept' ], )
        
            # Solution のリストに加えて更新する
            result                      |= self._updateSolution( col[ 1 ], True )
            
        # 'X' で始まる Reject / No response 行の時 - Solution のリストを REJECT で更新する
        elif col[ 0 ] == 'X' and ( 'Reject' in line or 'No response' in line ) and self._wait :
        
            # Reject 数を更新する　
            self._status[ 'reject' ]    += 1
            self._wait                  -= 1
            result[ 'reject' ]          = '{:010}'.format( self._status[ 'reject' ], )
        
            # Solution のリストに加えて更新する
            result                      |= self._updateSolution( col[ 1 ], False )
            
        # ' m' で始まるハッシュレートの時 - ハッシュレートを更新する
        elif col[ 0 ] == 'm' :
            result[ 'rate' ]            = '{} {}'.format( col[ 4 ], col[ 5 ], )
    
        return result

    #
    # サポート処理
    #

    # コマンドからの行の読み込み処理
    def             read( self, ) -> str or None :
        """
        コマンドからの行を読み込み、読めれば行を返す

        :return:        インスタンスがあれば True
        """

        # コマンド起動していない時は状況も変化しないので何もしない
        if not self.isAlive() :
            return None

        # コマンド出力があるかをを読んでみる
        line                    = self._miner.read( timeout = 100 )

        # ログ表示 - デバッグ用
        # print( line )
        
        return line


    # マイニングインスタンスのチェック処理
    def             isAlive( self, ) -> bool :
        """
        マイニングインスタンスがあるか（開始前か）を返す

        :return:        インスタンスがあれば True
        """

        # マイニングインスタンスがあれば True を返す
        return False if self._miner is None else True

    #
    # ソリューションリスト管理
    #

    # 実行ステータス
    _status: dict[ str, int or dict ] = { }

    # ソリューション行 { solution : str, result : str } のリスト、最新 10 個
    _solutions: list[ dict[ str, str or bool ] ] = [ ]
    _wait: int = 0

    # ソリューションリストの追加処理
    def             _addSolution( self, time : str, sol : str ) -> dict :
        """
        ソリューションリストに新しいデータを追加する

        :param time:    計算時間
        :param sol:     ソリューション値
        :return:        更新データ
        """

        # ソリューションをリスト先頭に設定する
        self._solutions.insert( 0, { 'time' : time, 'solution' : sol, } )

        # ソリューションのリストが 10 を超えている時はリスト末尾の Solution 行は削除する
        if len( self._solutions ) > 10 :
            self._solutions.pop()
            
        return self._getSolutionList()
        
    # ソリューションリストの追加処理
    def             _updateSolution( self, time : str, result : bool ) -> dict :
        """
        ソリューションリストに新しいデータを追加する

        :param time:    計算時間
        :param result:  True : 'ACCEPT' | False : 'REJECT'
        :return:        更新データ
        """

        # ソリューションリストのもっとも古い、まだ result のない行に結果をつける
        for i in range( len( self._solutions ) - 1, -1, -1 ) :
            
            # result のない行を見つける
            if not 'result' in self._solutions[ i ] :
                self._solutions[ i ][ 'time' ]          = time
                self._solutions[ i ][ 'result' ]        = result
                break
                
        # 更新した内容で更新する
        return self._getSolutionList()
        
        
    # ソリューションリストの更新データへの変換処理　
    def             _getSolutionList( self, ) -> dict :
        """
        ソリューションリストを更新データに変換する

        :return:        更新データ
        """
        
        # ソリューションのリストを画面の更新データに直して返す
        result          = {}

        # ソリューションのリストから sol 行データを設定する
        for i in range( 0, len( self._solutions ) ) :
            
            # ソリューション行のデータを得る
            item            = self._solutions[ i ]
            
            # ソリューション行のデータをリストの行（文字列）にする
            line            = {
                'text' : '{} : Solution = {}'.format( item[ 'time' ], item[ 'solution' ] ),
                'background_color' : None,
            }

            # result があれば、それもリストの行加え、色も変える
            if 'result' in item :
                line[ 'text' ]      += ' -> Result = {}'.format(
                    'OK, Accepted !!!!!' if item[ 'result' ] else 'Oops, Rejected ...'
                )
                line            |= { 'background_color' : BLUE if item[ 'result' ] else YELLOW }
                
            # なければ result 待ち、色を変える
            else :
                line            |= { 'background_color' : GREEN }

            # 画面の更新データにリストの行を追加する
            result[ 'sol' + str( i ) ]      = line

        return result
