/*
 Navicat Premium Data Transfer

 Source Server         : local
 Source Server Type    : MySQL
 Source Server Version : 80025
 Source Host           : localhost:3306
 Source Schema         : bd_spider

 Target Server Type    : MySQL
 Target Server Version : 80025
 File Encoding         : 65001

 Date: 26/01/2024 14:58:16
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for company_log
-- ----------------------------
DROP TABLE IF EXISTS `company_log`;
CREATE TABLE `company_log`  (
  `id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `status` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `date` datetime(0) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of company_log
-- ----------------------------
INSERT INTO `company_log` VALUES ('1f9f87b7-c73c-406a-b8cb-0316a95ccebf', '华领医药技术（上海）有限公司', 'error:HTTPConnectionPool(host=\'127.0.0.1\', port=10809): Read timed out. (read timeout=10)', '2024-01-25 16:39:25');
INSERT INTO `company_log` VALUES ('34ac5204-1cc4-4eb8-93b1-fdce7f851191', '华勤技术股份有限公司', 'error:HTTPConnectionPool(host=\'127.0.0.1\', port=10809): Read timed out. (read timeout=10)', '2024-01-25 16:39:38');
INSERT INTO `company_log` VALUES ('3c2dce3b-8ed1-4ea4-8dbf-6208063f98e6', '上海汇德汽车服务有限公司', 'error:HTTPConnectionPool(host=\'www.baidu.com\', port=80): Read timed out.', '2024-01-25 17:54:48');
INSERT INTO `company_log` VALUES ('9be00eba-54b4-470e-84cf-76d0e592f6c7', '益科博能源科技（上海）有限公司', 'error:HTTPConnectionPool(host=\'www.baidu.com\', port=80): Read timed out.', '2024-01-25 17:48:57');
INSERT INTO `company_log` VALUES ('affb67e2-9dac-454b-8304-3d267e5e2a42', '上海微创医疗器械（集团）有限公司', 'error:HTTPConnectionPool(host=\'www.baidu.com\', port=80): Max retries exceeded with url: /s?tn=news&wd=%E4%B8%8A%E6%B5%B7%E5%BE%AE%E5%88%9B%E5%8C%BB%E7%96%97%E5%99%A8%E6%A2%B0%EF%BC%88%E9%9B%86%E5%9B%A2%EF%BC%89%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8&pn=0&rtt=4&medium=0&cl=2 (Caused by NewConnectionError(\'<urllib3.connection.HTTPConnection object at 0x0000026BCA017CA0>: Failed to establish a new connection: [Errno 11001] getaddrinfo failed\'))', '2024-01-25 17:16:29');
INSERT INTO `company_log` VALUES ('c3d4e45d-becc-4f26-84ae-7e9f10dfbe2b', '苏州杰皓医疗技术有限公司', 'error:HTTPConnectionPool(host=\'www.baidu.com\', port=80): Read timed out.', '2024-01-25 17:16:00');
INSERT INTO `company_log` VALUES ('f82cce83-0d41-4094-8260-b0ba8d9637b8', '华存数据信息技术有限公司', 'error:HTTPConnectionPool(host=\'127.0.0.1\', port=10809): Read timed out.', '2024-01-25 16:39:02');

SET FOREIGN_KEY_CHECKS = 1;
