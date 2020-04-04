#日期：3.30~4.3
#主多：无；主空：棕榈，苹果，鸡蛋，棉花，沪镍，橡胶
#NOTICE：关注策略输入品种更新和主力合约切换
# 本周棕榈，铁矿等品种都会完成主力合约切换，策略执行要添加准主力合约
#若有更新要关注log，不要因笔误而导致策略没有正确执行

# 棕榈 - 已完成2波及以上空，目前突破10日线第一波反弹中；->p2009
#      - 第一波两浪多后的空机会，不存在两波多后的空机会
# 鸡蛋 - 还在第一波空中，还未进入主力合约切换周迹象
#      - 下地狱 | 双鬼
# 苹果 - 已完成2波空，止跌第一波反弹中；未进入主力合约切换周期
#      - 一波两浪多后的空机会 | 双鬼
# 棉花 - 第二波主空止跌期，主力合约切换周-> CF009
#      - 无，当前就在双鬼后的做空期，预计上半周有一些空机会
# 沪镍 - 第一波小空止跌期, ni2006合约正在主力合约期
#      - 下地狱 | 双鬼
# 橡胶 - 第二波止跌期，已完成主力合约切换， 当前SHFE.ru2009
#      - 下地狱
# 铁矿 - 日k周k都是均线上下震荡期，主力合约切换周 -> DCE.i2009
#      - 无策略型机会，无震荡模型机会；先观察两天，铁矿策略见每日复盘
#      - 4.1 铁矿承压破位中，逼阴标的或趋空标的

#1.1 下地狱：关注未完成2波及以上空的主空品种
# 3.31 镍和鸡蛋已过趋空期，在低位震荡期；橡胶同理
# 4.1 不管趋势好坏，信号都要发现：橡胶和郑棉
#/d/Anaconda3/python xiadiyu.py --SYMBOL DCE.jd2005
#/d/Anaconda3/python xiadiyu.py --SYMBOL SHFE.ni2006CF
/d/Anaconda3/python xiadiyu.py --SYMBOL SHFE.ru2009
/d/Anaconda3/python shuanggui.py --SYMBOL CZCE.CF005

#1.2 双鬼拍门：关注第一波空和第二波空未止跌的品种i
# 3.31同上，已没有主空品种，都是完成2波空后在处于低位震荡期和反弹期
# 4.1 铁矿再次破位，偏空趋势已成
/d/Anaconda3/python shuanggui.py --SYMBOL DCE.i2009
#/d/Anaconda3/python shuanggui.py --SYMBOL CZCE.AP005
#/d/Anaconda3/python shuanggui.py --SYMBOL SHFE.ni2006

#1.3 佛回头：主空偏空品种充分反弹滞涨后转空信号，当前没有处于弱势反弹高位的偏空品种
# 09合约偏空些，暂时加上，预计即使有此策略型机会，也要到下周开始了
#/d/Anaconda3/python fohuitou.py --SYMBOL DCE.i2009

#1.4 夸父逼阴：主空品种刚破位后的追空
# 大多已完成2波及以上空，同佛回头，暂且加上DCE.i2009,但从中强支撑看空间不大，铁矿暂时不会有逼阴机会
/d/Anaconda3/python biyin.py --SYMBOL DCE.i2009 --ZC1 540 --ZC2 460

#2.1 步步高：无
#2.2 夸父追阳：无
#2.3 弩末：无

#3.1 震荡品种两波多滞涨：无
#3.2 偏空震荡品种1波两浪多：主空品种急反弹后的空行情
#3.31 预计下周开始都会主抓这类机会
#4.1 棕榈一波两浪空由05合约完成，09合约第一波多后就破位了
#/d/Anaconda3/python yiboduo.py --SYMBOL DCE.p2009
#/d/Anaconda3/python yiboduo.py --SYMBOL CZCE.AP005

if test ! -z "$(cat /e/proj-futures/logs/"`date +%Y%m%d.log`" |grep error)"; then
    echo "Unexpected errors."
else
    if  test ! -z "$(cat /e/proj-futures/logs/"`date +%Y%m%d.log`" |grep Starting)"; then
        cat /e/proj-futures/logs/"`date +%Y%m%d.log`" |grep MYSTRATEGY > /e/proj-futures/output/"`date +strategy-%Y%m%d.txt`"
    fi
fi