# POST_PUSH_READBACK — round-20261021-r11

## 1. Push 與 readback（實測）

```
$ git -c credential.helper= -c core.askPass=<askpass helper> -c credential.interactive=always \
    push https://shw097-team@github.com/shw097-team/SBL.git HEAD:refs/heads/evidence/r11-20261021-intake
 * [new branch]      HEAD -> evidence/r11-20261021-intake

$ git ls-remote https://github.com/shw097-team/SBL refs/heads/evidence/r11-20261021-intake
4cd72b25be64ea115f6e23cc1a2d3c1f666353e0	refs/heads/evidence/r11-20261021-intake
$ git rev-parse HEAD
4cd72b25be64ea115f6e23cc1a2d3c1f666353e0
```

- 遠端 SHA == 本地 SHA ⇒ 推送持久化成立。
- 主幹 `main@345b9477` 與 tags `v0.1.0-foundation-preview` / `v0.1.1rc1` **未變更**（本輪只新增 evidence 分支）。
- 未使用 `--force`；未 `git add -A`；未 stage 他人 untracked 檔。
- token 只由 askpass helper 從 `API KEY/GITHUB-REPO_SHW097-4.txt` 讀出交給 git，未進 argv / log / commit。

## 2. 本 packet 各檔 digest（供 custody 比對）

| file | bytes | sha256 |
|---|---:|---|
| `00_ROUND_PLAN.md` | 20277 | `6867f8ae46388d81a8a8506957df2bf656710f35ee0e8c53d041aac4204fa330` |
| `10_BASELINE.md` | 5856 | `89f63b186201bf99d14bd1dab4297c7a365eda0fe830ac2720595ffa8b4ee885` |
| `20_SOURCE_LEDGER.json` | 12057 | `d3fc8329fe909963e8f104b2d04725169a10d4d156eadf8c110f7c59322c17d8` |
| `30_MANDATE_CHAIN.md` | 3562 | `24d2cc3f9919aebbfa0be0b39351bf25cae43327ce7860503225bcc05b34f513` |
| `40_FINDINGS.md` | 7944 | `08acd3be4e724c0cb301551d5f253fdbed74c727c90a229def73066d2596dd95` |
| `50_RETURN.json` | 8759 | `5d2066bdff3788a3c976f2def04d35c6a974185c6082508ba560e7da070bf33d` |
| `README.md` | 2952 | `6f04f4a2b2a8871f20bc2f2b00d367b97823c1adb4fcc7da1af921d650a3edd5` |
| `compile_control/compiler-receipt.json` | 552 | `51e5080020d6e18fca70bd268d2c4494d3f0eb38f45231150be431f5c2e1af00` |
| `compile_control/compiler-report.json` | 234 | `bf808b459b6631368226f135dfa01f7fa69afcb9839a55c3ff7e0853faa48568` |
| `hgk_conformance.log` | 2930 | `6d72f6b7575681ea232d7cba56fe6e60c5e654d49946ec7d991163888ca160e3` |
| `host_readback/sbl_harness_doctor.json` | 2498 | `c2568966a00a810328d62c1f966f0413b70f5e464f94526a7c676132d6ac8cf3` |
| `host_readback/sbl_stack_status.json` | 336 | `61859b71e83c352b9ca7193f4be907ada5a7bbaf25e62ee622f6fe6b879d0d8a` |
| `mandate_probes/EXECUTE_deepseek.json` | 5683 | `8ac14b6461c7f013796fb7b79b480bef50b6310b638e3304971492498a93c4ca` |
| `mandate_probes/PLAN_gpt61.json` | 5510 | `084747f30d9bac6f024fc50d221d66969379166b9cc81896887600ad2e8790a9` |
| `mandate_probes/VERIFY_gpt61.json` | 5532 | `3576c4d2088be929110b9d2bc39ba72b8e7ee01f0b1e7be4b8d779c6da3e2d99` |
| `mandate_probes/logs-EXECUTE/attempt-15872-1792595496-1-stderr.txt` | 220 | `c781d4e2f1a77065574b455bdc4460d84eb8fbb7c6b93b08c88b015d92373ba2` |
| `mandate_probes/logs-EXECUTE/attempt-15872-1792595496-1-stdout.txt` | 376 | `912406a2e55a7a1f7486a981724fbe6e2fd4614030eb8302aaf11611b04a600b` |
| `mandate_probes/logs-PLAN/attempt-14588-1792595485-2-stderr.txt` | 220 | `a4f060211d4deb06b9df94110db0f5b3c747ad61b8cd44244497c66eb065c6f4` |
| `mandate_probes/logs-PLAN/attempt-14588-1792595485-2-stdout.txt` | 571 | `398842e8234585a9e19499209c790db568c0c989747920be12ed1d49f100c2d6` |
| `mandate_probes/logs-VERIFY/attempt-21540-1792595500-1-stderr.txt` | 220 | `6b6ef8a4f2131a1f537dd089fba3221cff1e738302a1f23bddee9ab5163c36ae` |
| `mandate_probes/logs-VERIFY/attempt-21540-1792595500-1-stdout.txt` | 572 | `388caa9b6fc510c03a3647233e395ee52ba42b3274dcbb82869660688052e2d3` |
| `verifier_output.txt` | 1064 | `1c2c3f2c76056c824884e739872ba4d6e691ca17a2209648295c22cf5e0ff6a8` |
| `verify_r11_packet.py` | 3660 | `43e0b50287a9c0a87f512733a2145cb7d00ee7c481d0c0a47a050171154921e4` |

## 3. 驗證器可重跑

`python verify_r11_packet.py --ledger 20_SOURCE_LEDGER.json --docs-dir <DOC dir> --mirror-dir <mirror> --kp-dir <KP pack>` → `verifier_output.txt` 記錄 `PASS` / rc 0。

## 4. 主張邊界

本 packet 只證來源身份、bundle 可用性、環境分母與車道 mandate；`SBL_FULL_PRODUCT` 仍 **OPEN**。
