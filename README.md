# streamlit-map-template
我们使用了streamlit-map-template的多网页模版。

## 开发目标

构建一个基于 [SUMO](https://www.eclipse.dev/sumo/) 的交通仿真 Web 应用，支持：

- OSM 地图导入与仿真；
- 轨迹与交通指标的动态可视化；
- 多源交通数据融合；
- 面向研究与管理的高级分析功能；
- 易用的图形界面，支持国际化；
- 支持生成报告、动态图、视频等；
- 考虑软著、技术保护、Docker、数据导出、分析插件化等扩展。

## 总体开发思路

- **先做宽**：功能模块覆盖广，突出“别人没有的功能”。
- **再做深**：提升现有功能质量，强化分析能力。
- **能申请软著的先申请**。
- **前期可使用 Streamlit 快速开发 MVP**，后期可转为更稳定框架（如FastAPI+Vue）。
- **模块化开发，便于并行开发与维护**。
- **代码与功能文档同步撰写**。



## 项目结构建议



A streamlit template for mapping applications. It can be deployed to [Streamlit Cloud](https://streamlit.io/cloud).

Web App URL: <https://map-template.streamlit.app>

## Instructions

1. For the GitHub repository or use it as a template for your own project.
2. Customize the sidebar by changing the sidebar text and logo in each Python file.
3. Find your favorite emoji from https://emojipedia.org.
4. Add a new app to the `pages/` directory with an emoji in the file name, e.g., 1_🚀_Chart.py.

## Demo

![](https://i.imgur.com/6lj0oAO.png)
