
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
    パスワードジェネレータ主処理

    ethminer コマンドを利用してマイニングを実行します

    :param title:        ウィンドウのタイトル
    """

    # ロガー
    log             = Log( __name__ )

    # 主画面のレイアウトにより window を生成する
    screen          = 'main'
    win             = window( title = title, screen = 'main', )
    
    # コマンドの実行インスタンスを作る
    miner           = Miner()

    # イベントループ
    while True :

        # 画面からのイベントをポーリングし、発生したイベントとフォーム (入力データの辞書) を得る
        event, values   = win.read( timeout = 100, timeout_key = '_', )
        
        # DEBUG : タイムアウト以外のイベントをトレース
        if not event == '_' :
            log.debug( '受信データ : {}, {}'.format( event, str( values ) ) )

        # イベント毎の処理を行う
        try :
    
            # イベントに応じたアクションを実行し、画面を更新するための結果を得る
            result       = miner.do( screen, event, values )

            # 更新がなければ次のポーリングへ
            if result == {} :
                continue

            # DEBUG : タイムアウト以外の結果をトレース
            log.debug( '結果データ : ' + str( result ) )
            
            # event が None ならウィンドウを閉じる
            if result is None :
                break

            # 返ってきた結果で画面を更新する
            update( win, result )

        # バリデーションおよびアクションの例外は、エラーメッセージを表示する
        except Exception as e :
            abort( '!!! エラーが発生しました ({})'.format( e ) )

    # ウィンドウを終了
    win.close()
    
    
# 画面の更新処理
def             update( win : S.Window, result : dict ) -> None :
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


# エントリポイント
if __name__ == '__main__':
    
    # ロガーのセットアップ
    SetupLog( DEBUG )
    
    # ロガーのセットアップ
    Props.setup()
    
    # 主処理
    pyEthminer( 'ethminer - イーサリウムマイナー' )
