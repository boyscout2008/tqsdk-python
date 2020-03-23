#日期：3.23
#主多：无；主空：棕榈，苹果，鸡蛋，棉花，沪镍，橡胶
#NOTICE：关注策略输入品种更新和主力合约切换
#若有更新要关注log，不要因笔误而导致策略没有正确执行

#1.1 下地狱: 关注未完成2波及以上空的主空品种
# *棕榈 - 已完成2波及以上空，谨慎关注
# *鸡蛋 - 还在第一波空中，可考虑
# *苹果 - 已完成2波空，止跌中，谨慎关注
# 棉花 - 第二波主空中，暂时不关注
# 沪镍 - 第一波空中，暂时不关注
# 橡胶 - 第二波空中，暂时不关注
/d/Anaconda3/python xiadiyu.py --SYMBOL DCE.p2005
/d/Anaconda3/python xiadiyu.py --SYMBOL CZCE.AP005
/d/Anaconda3/python xiadiyu.py --SYMBOL DCE.jd2005

#1.2 双鬼拍门：关注第一波空和第二波空未止跌的品种
# 棕榈 - 2波及以上空止跌中，不关注
# *鸡蛋 - 还在第一波空中，可考虑
# 苹果 - 已完成2波空，止跌中，不考虑
# *棉花 - 第二波主空中，可关注
# *沪镍 - 第一波空中，可关注
# *橡胶 - 第二波空中，可关注
/d/Anaconda3/python shuanggui.py --SYMBOL DCE.jd2005
/d/Anaconda3/python shuanggui.py --SYMBOL CZCE.CF005
/d/Anaconda3/python shuanggui.py --SYMBOL SHFE.ni2006
/d/Anaconda3/python shuanggui.py --SYMBOL SHFE.ru2005

#1.3 佛回头：主空偏空品种充分反弹滞涨后转空信号，当前没有处于弱势反弹高位的偏空品种
#3.24 铁矿转空中，后续可考虑逼阴，现在优先考虑佛回头
/d/Anaconda3/python fohuitou.py --SYMBOL DCE.i2005

#1.4 夸父逼阴：主空品种刚破位后的追空
# 大多已完成2波及以上空
# *沪镍 - 刚破新低，可考虑，但逼阴信号日已过，现在该遵循双鬼做空它
#/d/Anaconda3/python ../biyin.py --SYMBOL SHCE.ni2006
#3.24 铁矿转空中，后续可考虑逼阴，现在优先考虑佛回头
/d/Anaconda3/python ../biyin.py --SYMBOL DCE.i2005 --ZC1 606 --ZC2 570

#2.1 步步高：无，偏多震荡品种可以考虑做第二波多
#2.2 夸父追阳：无
#2.3 弩末：无

#3.1 震荡品种两波多滞涨：无
#3.2 偏空震荡品种1波两浪多：无

if test ! -z "$(cat /e/proj-futures/logs/"`date +%Y%m%d.log`" |grep error)"; then
    echo "Unexpected errors."
else
    if  test ! -z "$(cat /e/proj-futures/logs/"`date +%Y%m%d.log`" |grep Starting)"; then
        cat /e/proj-futures/logs/"`date +%Y%m%d.log`" |grep MYSTRATEGY > /e/proj-futures/output/"`date +strategy-%Y%m%d.txt`"
    fi
fi