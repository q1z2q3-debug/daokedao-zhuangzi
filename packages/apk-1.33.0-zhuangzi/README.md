# 道可道·庄子 离线 APK v1.33.0

- 文件：`道可道-庄子-1.33.0.apk`
- 体量：3,687,458 B（3.5 MB）
- 包名：`com.daokedao.zhuangzi`　versionCode 13300　versionName 1.33.0
- targetSdk 34 / minSdk 21
- 权限：**零**（manifest 无 `uses-permission`，壳内 `setBlockNetworkLoads(true)`）
- 签名：v1 / v2 / v3 全通过，证书 SHA-256 `2BDC2468…6CEA`（与《易传》《道德经》同一密钥，可长期覆盖升级）
- SHA-256：见 `SHA256SUMS`

内容：内七篇全帙＋外杂篇选读，35 卷；正文 972,593 B 与思源宋体子集两字重（3,737 用字）全部内置于 assets，断网可读。
构建：`cd apk-zhuangzi && python3 prepare-assets.py && SDK=/tmp/apkbuild BUILD_TOOLS=… bash build.sh`
