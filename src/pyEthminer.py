
"""
pyEthminer - Ethminer のマイニング制御・モニタを行う GUI プログラム
"""

# インポート
import          PySimpleGUI                 as          S

# noinspection PyUnresolvedReferences
from            common.Log                  import      SetupLog, Log, abort, INFO, DEBUG
from            common.Props                import      Props

from            Layout                      import      window
from            Miner                       import      Miner

# Ethminer 実行 - 主処理
def         pyEthminer( title : str ) -> None :
    """
    イーサリウムマイニング GUI 主処理

    GUI 経由で ethminer コマンドを利用してマイニングを実行します

    :param title:        ウィンドウのタイトル
    """

    # ロガー
    log             = Log( __name__ )

    # 主画面のレイアウトにより window を生成する
    screen          = 'main'
    win             = window( title = title, screen = 'main', )
    
    # コマンドの実行インスタンスを作る
    miner           = Miner()
    
    # コマンド動作一時停止中
    paused          = False

    # イベントループ
    while True :

        # 画面からのイベントをポーリングし、発生したイベントとフォーム (入力データの辞書) を得る
        event, values   = win.read( timeout = 100, timeout_key = '_', )
        
        # イベント毎の処理を行う
        try :
    
            # DEBUG : タイムアウト以外のイベントをトレース
            if not event == '_' :
                log.debug( '受信データ : {}, {}'.format( event, str( values ) ) )
                
            # イベントに応じたアクションを実行し、画面を更新するためのデータを得る
            result       = _do( screen, event, values, miner )

            # event が None なら終了処理を行ってからウィンドウを閉じる
            if result is None :
                _closing( win, miner )
                break

            # DEBUG : 更新データがあればトレース
            if not result == {} :
                log.debug( '結果データ : ' + str( result ) )
            
            # 返ってきた更新データで画面を更新する
            _update( win, result )

        # バリデーションおよびアクションの例外は、エラーメッセージを表示する
        except Exception as e :
            abort( '!!! エラーが発生しました ({})'.format( e ) )

    # ウィンドウを閉じる
    return None


# マイニングコマンドの制御アクション処理
def             _do( screen : str, event : str, _ : dict, miner : Miner ) -> dict[ str, str or dict ] or None :
    """
    マイニングコマンドの制御アクション処理

    イベントに対応するアクションを実行し、実行結果を更新データとして返す

    :param screen:      画面名
    :param event:       発生したイベント名
    :param miner:       コマンド実行インスタンス
    :return:            結果としてのフォーム更新データ（文字列またはフィールド名と値の組）。None なら終了を示す
    """
    
    # アクションの結果領域
    result          = {}
    
    # main・start - マイニングコマンドを開始する
    if screen == 'main' and event == 'start' :
        result          = miner.start()
    
    # main・_ - 画面イベントタイムアウト
    elif screen == 'main' and event == '_' :
        result          = miner.status()

        # 停止完了のチェックをする（停止待ちでないなら何もしない）
        result          |= miner.wait_stop()

    # main・pause - マイニングコマンドを一時停止・再開する
    elif screen == 'main' and event == 'pause' :
        result          = miner.pause()
    
    # main・stop - マイニングコマンドを停止する
    elif screen == 'main' and event == 'stop' :
        result          = miner.stop()
    
    # main・close - ウィンドウを終了する
    elif ( screen == 'main' and event == 'close' ) or event is None :
        return None
    
    # 対応するアクションがなければメッセージを出す
    else :
        result[ 'msg' ] = '!!! 画面 {} イベント {} が定義されていません'.format( screen, event )

    # 結果 (画面の更新データ) を返す - None を返すと window は終了する
    return result


# 画面の更新処理
def             _update( win : S.Window, result : dict ) -> None :
    """
    画面の更新を行う
    パスワードジェネレータ主処理

    ethminer コマンドを利用してマイニングを実行します

    :param win:      i  更新対象ウィンドウ
    :param result:      更新データ
    """

    # 返ってきた結果の組すべてで画面を更新する
    for key, val in result.items() :
    
        # 文字列が返れば、エレメントの値をアップデートする
        if isinstance( val, str ) :
            win[ key ].update( val )
    
        # 辞書が返れば 、エレメントの属性を展開してアップデートする
        elif isinstance( val, dict ) :
        
            # エレメントの値と属性でアップデートする : 値の文字列はキー text で指定する
            if 'text' in val :
                win[ key ].update( val.pop( 'text' ), ** val )
        
            # エレメントの属性でアップデートする
            else :
                win[ key ].update( ** val )


# ウィンドウの終了時処理
def             _closing( win: S.Window, miner: Miner ) -> None :
    """
    ウィンドウの終了時のコマンド停止処理を行う

    :param win:         ウィンドウ
    :param miner:       コマンドの実行インスタンス
    """
    
    # コマンド起動中なら停止してから終了する
    if miner.isAlive() :
        
        # コマンドを停止する
        _update( win, miner.stop( 'コマンド動作中です' ) )
        win.refresh()
        
        # コマンドの終了を待つ
        while miner.isAlive() :
            miner.wait_stop()
    
    # ウィンドウを終了
    win.close()


# エントリポイント
if __name__ == '__main__':
    
    # ロガーのセットアップ
    SetupLog( DEBUG )
    
    # ロガーのセットアップ
    Props.setup()
    
    # 主処理
    pyEthminer( 'ethminer - イーサリウムマイナー' )
