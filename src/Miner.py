
"""
Miner.py

        画面・イベントごとにアクションを行い、その結果を返す
"""

# インポート
from            threading               import      Thread

from            common.Log              import      Log
from            common.Props            import      Props
from            common.CommandExecutor  import      CommandExecutor

from            Layout                  import      _GREEN, _RED, _YELLOW, _BLUE

# マイニングコマンドの実行クラス
class           Miner :
    """
    マイニングコマンドの実行クラス
    """

    # コンストラクタ
    def             __init__( self, ) :
        """
        コンストラクタ
        """
        
        # コマンド実行インスタンス
        self._miner : CommandExecutor or None                   = None

        # コマンド
        self._cmd : str                                         = Props.props( 'MINER', 'CMD' )
        
        # 接続先プール
        self._pool : str                                        = (
            Props.props( 'POOL', 'PROTOCOL' )
                + '://' + Props.props( 'POOL', 'USER' ) + '.' + Props.props( 'POOL', 'WORKER' )
                + '@' + Props.props( 'POOL', 'HOST' )
        )

        # オプション引数
        self._opts : list                                       = (
            [ *Props.props( 'MINER', 'OPTIONS' ).split(), '-P', self._pool ]
        )

        # コマンド一時停止中
        self._paused : bool                                     = False

        # コマンド停止スレッド
        self._stopper : Thread or None                          = None

        # 実行ステータス
        self._status : dict[ str, int or dict ]                 = (
            { 'job' : 0, 'accept' : 0, 'reject' : 0, 'sols' : [] }
        )

        # ソリューション行 { solution : str, result : str } のリスト、最新 10 個
        self._solutions : list[ dict[ str, str or bool ] ]      = []

        # ソリューション行に対する結果待ち数
        self._wait : bool                                       = False

    #
    # コマンド制御
    #

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
        result[ 'start' ]   = { 'disabled' : True  }
        result[ 'pause' ]   = { 'disabled' : False }
        result[ 'stop'  ]   = { 'disabled' : False }
    
        result[ 'rate'  ]   = { 'text' : '', 'background_color' : _GREEN }

        result[ 'pool'  ]   = self._pool
        
        result[ 'msg'   ]   = 'マイニング中です...'
        
        # 結果待ち数をリセットする
        self._wait          = False

        # 更新データを返す
        return result


    # マイニングコマンドの一時停止・再開処理
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

        # 一時停止中の時、再開する
        if self._paused :

            # コマンドを再開する
            self._miner.resume()

            result[ 'start' ]   = { 'disabled' : True }
            result[ 'pause' ]   = { 'text' : ' 一時停止 ', 'disabled' : False, }
            result[ 'stop'  ]   = { 'disabled' : False }

            result[ 'rate'  ]   = { 'text' : '', 'background_color' : _GREEN }

            result[ 'msg'   ]   = 'マイニング中です...'
            
            self._paused        = False

        # 実行中の時、一時停止する
        else :
            
            # コマンドを一時停止する
            self._miner.pause()

            # 画面の更新データを設定する
            result[ 'start' ]   = { 'disabled' : True  }
            result[ 'pause' ]   = { 'text' : '  再  開  ', 'disabled' : False }
            result[ 'stop'  ]   = { 'disabled' : False }
            
            result[ 'rate'  ]   = { 'text' : '', 'background_color' : _YELLOW }

            result[ 'msg'   ]   = '一時停止しています...'

            self._paused        = True
        
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



    # マイニングコマンドの停止処理
    def             stop( self, msg : str = None ) -> dict :
        """
        マイニングコマンドを別スレッドで停止する

        :param msg:     停止事由
        :return:        実行結果の更新データ
        """
    
        # 結果領域
        result              = {}

        # 起動していない時はメッセージを出す
        if not self.isAlive() :
            result[ 'msg' ]     = '!!! コマンドが起動していません'
            return result

        # コマンドを停止する - 停止まで時間がかかるので別スレッドとする
        self._miner.resume()
        self._stopper       = Thread( target = lambda : self._miner.terminate() )
        self._stopper.start()

        # 画面の更新データを設定する
        result[ 'start' ]   = { 'disabled' : True }
        result[ 'pause' ]   = { 'disabled' : True }
        result[ 'stop'  ]   = { 'disabled' : True }
        
        result[ 'rate'  ]   = { 'text' : '', 'background_color' : _RED }

        result[ 'pool'  ]   = ''

        result[ 'msg'   ]   = msg if msg else '' + '停止しています... (しばらくお待ちください)'
        
        return result


    # マイニングコマンドの停止待ち処理
    def             wait_stop( self, ) -> dict :
        """
        マイニングコマンドを別スレッドで停止されるのを待つ

        :return:        実行結果の更新データ
        """
    
        # 結果領域
        result              = {}
        
        # 停止待ちでなければ何もしない
        if not self._stopper :
            return result
            
        # 停止処理が終わったかをチェックする
        self._stopper.join( timeout = 100 / 1000.0 )
        
        # 終了したなら、停止スレッドとマイニングコマンドのインスタンスを消す
        if not self._stopper.is_alive() :
            self._miner         = None
            self._stopper       = None
            
            # 画面の更新データを設定する
            result[ 'start' ]   = { 'disabled' : False }
            result[ 'pause' ]   = { 'disabled' : True  }
            result[ 'stop'  ]   = { 'disabled' : True  }

            result[ 'rate'  ]   = { 'text' : '', 'background_color' : _RED }
            
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
        
        # EOF の時は、コマンドを止める
        if line == '' :
            result                  = self.stop( 'EOF を検出しました' )
            return result

        # 空文字列の時は何もしない
        if line is None :
            return result

        # 行をログして単語に分解する
        line                = line.replace( '\n', '' )
        
        # ログ行
        result[ 'log' ]     = line[ 21 : ]
        log.info( line )

        # DEBUG : 結果待ち中はログ
        if self._wait :
            print( line )

        # 行を単語に分割して解析する
        col                 = line.split()

        # 文字がない時は何もしない
        if len( col ) == 0 :
            return result
    
        # 'cl' で始まる Solution 行の時 -  Solution のリストに更新する
        if col[ 0 ] == 'cl' and line.find( 'Sol:' ) > 0 :
            self._wait                  = True
            result                      |= self._addSolution( col[ 1 ], col[ 4 ][ : -1 ], col[ 6 ] )
            print( line )

        # 'i' で始まる Job 行の時 - Job 行を更新する
        elif col[ 0 ] == 'i' and line.find( 'Job:' ) > 0 :
            self._status[ 'job' ]       += 1
            result[ 'job' ]             = '{:010} : {} : {}'.format( self._status[ 'job' ], col[ 1 ], col[ 3 ][ : -1 ], )
    
        # 'i' で始まる Accepted 行の時 - Solution のリストを ACCEPT で更新する
        elif col[ 0 ] == 'i' and '**Accepted' in line and self._wait :
        
            # Accept 数を更新する　
            self._status[ 'accept' ]    += 1
            self._wait                  = False
            result[ 'accept' ]          = '{:010}'.format( self._status[ 'accept' ], )
        
            # Solution のリストに加えて更新する
            result                      |= self._updateSolution( col[ 1 ], True )

        # 'X' で始まる行を結果待ち中に受ければリジェクト
        elif col[ 0 ] == 'X' and self._wait :

            # Reject 数を更新する　
            self._status[ 'reject' ]    += 1
            self._wait                  = False
            result[ 'reject' ]          = '{:010}'.format( self._status[ 'reject' ], )

            # Solution のリストに加えて更新する
            result                      |= self._updateSolution( col[ 1 ], False )

        # ' m' で始まるハッシュレートの時 - ハッシュレートを更新する
        elif col[ 0 ] == 'm' :
            color                       = _BLUE if float( col[ 4 ] ) > 2.0 and col[ 5 ] == 'Mh' else _GREEN
            result[ 'rate' ]            = {
                'text' : '{} {}'.format( col[ 4 ], col[ 5 ], ),
                'background_color' : color
            }

        # 更新データを返す
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

    # ソリューションリストの追加処理
    def             _addSolution( self, time : str, job : str, sol : str ) -> dict :
        """
        ソリューションリスト先頭に新しいデータを追加する

        :param time:    計算時間
        :param sol:     ソリューション値
        :return:        更新データ
        """

        # すでに同じ job があれば何もしない
        for s in self._solutions :
            if s[ 'job' ] == job :
                return {}

        # ソリューションをリスト先頭に設定する
        self._solutions.insert( 0, { 'time' : time, 'job' : job, 'solution' : sol, } )
 
        # ソリューションのリストが 10 を超えている時はリスト末尾の Solution 行は削除する
        if len( self._solutions ) > 10 :
            self._solutions.pop()
            
        return self._getSolutionList()
        
        
    # ソリューションリストの追加処理
    def             _updateSolution( self, time : str, result : bool ) -> dict :
        """
        ソリューションリスト先頭に結果を付加する

        :param time:    計算時間
        :param result:  True : 'ACCEPT' | False : 'REJECT'
        :return:        更新データ
        """

        # ソリューションリストのもっとも古い、まだ result のない行に結果をつける
        self._solutions[ 0 ][ 'time' ]          = time
        self._solutions[ 0 ][ 'result' ]        = result
        
        # 更新した内容で更新する
        return self._getSolutionList()
        
        
    # ソリューションリストの更新データへの変換処理　
    def             _getSolutionList( self, ) -> dict :
        """
        ソリューションリスト全体を更新データに変換する

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
                'text' : '{} : {} = {}'.format( item[ 'time' ], item[ 'job' ], item[ 'solution' ] ),
                'background_color' : None,
            }

            # result があれば、それもリストの行加え、色も変える
            if 'result' in item :
                line[ 'text' ]      += ' -> Result = {}'.format(
                    'OK, Accepted !!!!!' if item[ 'result' ] else 'Oops, Rejected ...'
                )
                line            |= { 'background_color' : _BLUE if item[ 'result' ] else _YELLOW }
                
            # なければ result 待ち、色を変える
            else :
                line            |= { 'background_color' : _GREEN }

            # 画面の更新データにリストの行を追加する
            result[ 'sol' + str( i ) ]      = line

        return result
