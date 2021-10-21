# framework-v2
随着比赛复杂度的不断提升，机器人的模式越来越多样，原有python架构中”armor“和”energy“的分类
已难以满足需求；同时，存在新人阅读代码困难、将自己的代码融入架构困难的问题。因此，在保证代码逻辑性
不被破坏的情况下，强化原有架构中面向对象的概念，从而寻求一种可读性和灵活性更强的架构。

## v2.0.1
1、加入./utils/options.py,使用**修饰器**解决debug_mode的问题，源码结构中仅使用”@debug_mode“（detect,py第13行）即可在不改变任何架构的基础上
选择是否包含此功能；  
2、./core中加入filter.py，但卡尔曼滤波还在调试中，未投入使用;  
3、template.py从/core中调整至/utils;  
4、原有的计算帧率的代码暂且放在main.py中，拟定移动至debug_mode中;  

###### 目录结构
├── README.md  
├── main.py  
├── core  
│   ├── armor_rotate.py  
│   ├── armor_stable.py  
│   ├── detect.py  
│   ├── mode_chooser.py  
│   └── filter.py  
├── config  
│   ├── BaseConfig.yaml  
│   ├── cap_configs.py  
│   ├── config.py  
├── device  
│   ├── caps.py  
├── utils  
│   ├── serials.py  
│   ├── time.py  
│   ├── options.py(v2.0.1)  
│   └── template.py   
├── template_image  
……  
├── video  
……  

### 预期效果  
可读性：通过阅读main.py和detect。py两个文档，协作者可以快速、高效地读懂其他人的算法实现思路；  
灵活性：在detect.py下，创作者可以交叉调用各个类下的api，因而轻松借鉴别人的代码；  

##### main.py  
1、红蓝方选择、是否开启debug、串口等功能；  
2、创建轮询串口接受信息的子线程；  
3、创建moder_chooser（实例），负责模式管理、功能切换；  
4、创建detect（实例），统筹各子功能的实现；  
5、串口发送信息；  

##### detect.py  
1、__init__:创建子模式的实例；（每个模式也以对象的形式定义）  
2、以简短清晰为原则，使用子模式下的函数，展现该功能的实现过程；  

##### 子模式：以armor_stable.py为例
1、roi、模板匹配的素材以属性的形式呈现；  
2、预处理、灯条筛选、装甲板匹配识别、弹道补偿、滤波器等算法以API的形式封装在该类下；

