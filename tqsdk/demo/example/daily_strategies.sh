#3.17~3.21
#主多：无；主空：棕榈，苹果，鸡蛋，郑棉
#步步高：无，偏多震荡品种可以考虑做第二波多
/d/Anaconda3/python bubugao.py --SYMBOL DCE.i2005
#下地狱: 没有完成两波空的主空品种，只有鸡蛋了
#/d/Anaconda3/python xiadiyu.py --SYMBOL DCE.p2005
#/d/Anaconda3/python xiadiyu.py --SYMBOL.CZCE.AP005
#/d/Anaconda3/python xiadiyu.py --SYMBOL CZCE.CF005
/d/Anaconda3/python xiadiyu.py --SYMBOL DCE.jd2005
#/d/Anaconda3/python xiadiyu.py --SYMBOL CZCE.SR005
#双鬼拍门：主空或偏空品种还在转空蓄势阶段和第一波空之后的品种只有鸡蛋，谨慎关注还未止跌的强空品种棕榈、棉花、苹果
/d/Anaconda3/python xiadiyu.py --SYMBOL DCE.jd2005
/d/Anaconda3/python shuanggui.py --SYMBOL DCE.p2005
/d/Anaconda3/python xiadiyu.py --SYMBOL CZCE.CF005
/d/Anaconda3/python xiadiyu.py --SYMBOL.CZCE.AP005
#佛回头
#夸父追阳
#夸父逼阴
#震荡品种两波多滞涨
#偏空震荡品种1波两浪多

if test ! -z "$(cat /e/proj-futures/logs/"`date +%Y%m%d.log`" |grep error)"; then
    echo "Unexpected errors."
else
    if  test ! -z "$(cat /e/proj-futures/logs/"`date +%Y%m%d.log`" |grep Starting)"; then
        cat /e/proj-futures/logs/20200316.log |grep MYSTRATEGY > /e/proj-futures/output/"`date +strategy-%Y%m%d.txt`"
    fi
fi