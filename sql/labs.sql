CREATE TABLE IF NOT EXISTS labs (
  id              BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
  name            VARCHAR(100) NOT NULL                COMMENT '实验室名称，唯一',
  description     TEXT                                 COMMENT '详细介绍（阶段三 RAG 也检索它）',
  location        VARCHAR(100) NOT NULL DEFAULT ''     COMMENT '位置，如 A 座 301',
  capacity        INT          NOT NULL DEFAULT 0      COMMENT '可容纳人数',
  open_time_start TIME         NOT NULL                COMMENT '开放开始时刻',
  open_time_end   TIME         NOT NULL                COMMENT '开放结束时刻',
  status          VARCHAR(20)  NOT NULL DEFAULT '开放中' COMMENT '开放中 | 维护中',
  PRIMARY KEY (id),
  UNIQUE KEY uk_labs_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='实验室表';

INSERT INTO labs (name, description, location, capacity, open_time_start, open_time_end, status) VALUES
('分子检测室',   '用于核酸提取、荧光定量 PCR 和基因测序，承接病原体核酸与用药相关基因检测', '检验楼 3 层 301', 8,  '09:00', '18:00', '开放中'),
('微生物检测室', '用于药品与临床样本的微生物限度、培养观察，配有生物安全柜和恒温培养箱',     '检验楼 3 层 302', 10, '09:00', '18:00', '开放中'),
('理化检测室',   '承担原料与成品的含量、有关物质和溶剂残留检测，主要仪器为液相色谱和气质联用', '检验楼 2 层 201', 12, '09:00', '21:00', '开放中'),
('免疫检测室',   '开展酶联免疫和化学发光检测，用于感染标志物、激素和肿瘤标志物筛查',           '检验楼 2 层 202', 16, '09:00', '21:00', '开放中'),
('样本前处理室', '负责样本接收、离心、分装和编号。当前设备校准，暂停开放',                     '检验楼 1 层 105', 8,  '09:00', '18:00', '维护中');

