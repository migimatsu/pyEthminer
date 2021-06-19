
"""
pyEthminer - Ethminer のマイニング制御・モニタを行う GUI プログラム
"""

# インポート
import          PySimpleGUI                 as          S
from            PySimpleGUI                 import Window

from            common.Log                  import      SetupLog, Log, abort, INFO, DEBUG
from            common.Props                import      Props

from            Layout                      import      layout
from            Miner                       import      Miner

# GUI の表示フォント
_FONT           = ( 'Anito', 14, )

# パスワードジェネレータ主処理
def         pyEthminer( title : str ) -> None :
    """
    パスワードジェネレータ主処理

    ethminer コマンドを利用してマイニングを実行します

    :param title:        ウィンドウのタイトル
    """

    # ロガー
    log         = Log( __name__ )

    # 主画面のレイアウトにより window を生成する
    screen          = 'main'
    window          = S.Window( title = title, layout = layout( screen ), font = _FONT, )
    
    # コマンドの実行インスタンスを作る
    miner           = Miner()

    # イベントループ
    while True :

        # 画面からのイベントをポーリングし、発生したイベントとフォーム (入力データの辞書) を得る
        event, values       = window.read( timeout = 100, timeout_key = '_', )
        
        # DEBUG : タイムアウト以外のイベントをトレース
        if not event == '_' :
            log.debug( '受信データ : {}, {}'.format( event, str( values ) ) )

        # イベント毎の処理を行う
        try :

            # イベントに応じたアクションを実行し、画面を更新するための結果を得る
            result          = miner.do( screen, event, values )

            # DEBUG : タイムアウト以外の結果をトレース
            if not result == {} :
                log.debug( '結果データ : ' + str( result ) )

            # 更新がなければ次の受信へ
            if result == {} :
                continue

            # None が返って来た時は終了する
            elif result is None :
                break

            # 返ってきた結果で画面を更新する
            update( window, result )

        # バリデーションおよびアクションの例外は、エラーメッセージを表示する
        except Exception as e :
            abort( '!!! エラーが発生しました ({})'.format( e ) )

    # ウィンドウを終了
    window.close()
    
    
# GUI 画面の更新処理
def             update( window : Window, result : dict ) -> None :
    """
    GUI 画面の更新を行う
    パスワードジェネレータ主処理

    ethminer コマンドを利用してマイニングを実行します

    :param window:      更新対象ウィンドウ
    :param result:      更新データ
    """

    # 返ってきた結果の組すべてで画面を更新する
    for key, val in result.items() :
    
        # 文字列が返れば、エレメントの値をアップデートする
        if isinstance( val, str ) :
            window[ key ].update( val )
    
        # 辞書が返れば 、エレメントの属性を展開してアップデートする
        elif isinstance( val, dict ) :
        
            # エレメントの値と属性でアップデートする : 値の文字列はキー text で指定する
            if 'text' in val :
                window[ key ].update( val.pop( 'text' ), ** val )
        
            # エレメントの属性でアップデートする
            else :
                window[ key ].update( ** val )


# エントリポイント
if __name__ == '__main__':
    
    # ロガーのセットアップ
    SetupLog( DEBUG )
    
    # ロガーのセットアップ
    Props.setup()
    
    # 主処理
    pyEthminer( 'ethminer - イーサリウムマイナー' )
