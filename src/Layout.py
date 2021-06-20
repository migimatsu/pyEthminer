
"""
Layout.py

        画面ごとのレイアウトを返す
"""

# インポート
import          copy

from            common.Log          import      abort
from            typing              import      List

import          PySimpleGUI         as          S

#
# デザインテーマの設定をする
#       レイアウトの定義より前にテーマを設定すること
#
S.theme( 'DarkGrey4' )

# 表示フォント
_FONT           = ( 'Anito', 14, )
_FONT_SOL       = ( 'Anito', 10, )
# _FONT           = ( 'Anito', 14, )
# _FONT_SOL       = ( 'Anito', 10, )

#
# 使う配色を設定する
#
BLACK       = '#000000'
RED         = '#BC3F3C'
GREEN       = '#32593D'
BLUE        = '#3993D4'
YELLOW      = '#A87B00'

#
# 画面のレイアウト
#       レイアウトは window に描画される毎に「使い捨て」になるので注意
#       このため、定義したレイアウトの deepcopy() をレイアウトとして返す
#

# 部分レイアウト - 制御ボタン
_MINER_BUTTON       = [
    [
        S.Button( '開始', key = 'start', disabled = False, disabled_button_color = BLACK, ),
        S.Button( '一時停止', key = 'pause', disabled = True, disabled_button_color = BLACK, ),
        S.Button( '再開', key = 'resume', disabled = True, disabled_button_color = BLACK, ),
        S.Button( '停止', key = 'stop', disabled = True, disabled_button_color = BLACK, ),
    ],
]

_WINDOW_BUTTON      = [
    [
        S.Button( '閉じる', key = 'close', disabled = False, ),
    ]
]

# 画面レイアウト
_LAYOUT             = {
    
    # 主画面のレイアウト
    'main' :
        
        [
            # 接続先プール
            [
                S.Text( 'プール', size = ( 20, 1 ), justification = 'right', ),
                S.Text( '', key = 'pool', size = ( 100, 1 ), justification  = 'center', ), ],
            # 状況
            [
                S.Text( 'ハッシュレート', size = ( 20, 1 ), justification  = 'right', ),
                S.Text( '', key = 'rate', size = ( 100, 1 ), justification  = 'center', background_color = RED ),
            ],
            [
                S.Text( 'Job :', size = ( 15, 1 ), justification = 'right', ),
                S.Text( '0000000000', key = 'job', size = ( 35, 1 ), ),
                S.Text( 'Accepted :', size = ( 15, 1 ), justification  = 'right', ),
                S.Text( '0000000000', key = 'accept', size = ( 15, 1 ), ),
                S.Text( 'Rejected :', size = ( 15, 1 ), justification  = 'right', ),
                S.Text( '0000000000', key = 'reject', size = ( 15, 1 ), ),
            ],
            # ソリューション表示 key = sol0 - sol9 の行
            * (
                [
                    S.Text( '', size = ( 40, 1 ), font = _FONT_SOL, ),
                    S.Text( '', key = 'sol' + str( i ), size = ( 100, 1 ),
                                                    justification = 'center', font = _FONT_SOL, ),
                ] for i in range( 0, 10 )
            ),
            # メッセージ表示
            [
                S.Text( '', key = 'msg', size = ( 132, 1 ), justification = 'center', ),
            ],
            # ログ表示 - デバッグ用
            # [
            #     S.Output( size = ( 132, 10 ), ),
            # ],
            # 制御ボタン
            [
                S.Text( '', size = ( 30, 1 ) ),
                S.Frame( ' マイニング ', _MINER_BUTTON, title_location = S.TITLE_LOCATION_LEFT ),
                S.Frame( ' ウィンドウ ', _WINDOW_BUTTON, title_location = S.TITLE_LOCATION_LEFT ),
            ]
        ],
}


# 画面名に応じたレイアウトを返す
def             window( title : str, screen : str ) -> S.Window :
    
    if screen == 'main' :
        return S.Window( title = title, layout = layout( screen ), font = _FONT, )
    

# 画面名に応じたレイアウトを返す
def             layout( screen : str ) -> List :
    """
    画面名に応じたレイアウトを返す

    :param screen:      画面名
    :return:            レイアウト
    """

    # 画面名に対応するレイアウトを返す
    try :

        # 画面に対応するレイアウトのディープコピーオブジェクトを返す
        return copy.deepcopy( _LAYOUT[ screen ] )

    # 対応する画面がなければ異常終了
    except Exception :
        abort( '!!! 画面 {} が定義されていません'.format( screen ) )
