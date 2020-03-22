#日期：xxx-xxx
#主多：xxx；主空：xxx
#NOTICE：关注策略输入品种更新和主力合约切换
#1.1 下地狱: xx,xx
#/d/Anaconda3/python ../xiadiyu.py --SYMBOL DCE.p2005
#/d/Anaconda3/python ../xiadiyu.py --SYMBOL.CZCE.AP005
#/d/Anaconda3/python ../xiadiyu.py --SYMBOL CZCE.CF005
#/d/Anaconda3/python ../xiadiyu.py --SYMBOL DCE.jd2005
#/d/Anaconda3/python ../xiadiyu.py --SYMBOL CZCE.SR005
#/d/Anaconda3/python ../xiadiyu.py --SYMBOL SHCE.ru001
#1.2 双鬼拍门：xx, xx
#/d/Anaconda3/python ../shuanggui.py --SYMBOL SHCE.ru001

#1.3 佛回头：主空偏空品种充分反弹滞涨后转空信号，当前没有处于弱势反弹高位的偏空品种
#/d/Anaconda3/python ../fohuitou.py --SYMBOL DCE.p2005

#1.4 夸父逼阴
#/d/Anaconda3/python ../biyin.py --SYMBOL DCE.p2005

#2.1 步步高：无，偏多震荡品种可以考虑做第二波多
#/d/Anaconda3/python ../bubugao.py --SYMBOL DCE.i2005
#2.2 夸父追阳
#2.3 弩末

#3.1 震荡品种两波多滞涨
#3.2 偏空震荡品种1波两浪多

if test ! -z "$(cat /e/proj-futures/logs/"`date +%Y%m%d.log`" |grep error)"; then
    echo "Unexpected errors."
else
    if  test ! -z "$(cat /e/proj-futures/logs/"`date +%Y%m%d.log`" |grep Starting)"; then
        cat /e/proj-futures/logs/20200316.log |grep MYSTRATEGY > /e/proj-futures/output/"`date +strategy-%Y%m%d.txt`"
    fi
fi