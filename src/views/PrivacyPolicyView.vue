<template>
  <div class="privacy-container">
    <!-- 顶部导航与操作栏 -->
    <header class="privacy-header">
      <div class="header-content">
        <div class="app-brand">
          <div class="app-logo">
            <span class="logo-emoji">🐾</span>
          </div>
          <div class="brand-text">
            <h1 class="brand-title">GouTou 应用隐私合规与权利保护中心</h1>
            <p class="brand-subtitle">适用于 GouTou（Android / HarmonyOS 鸿蒙移动端 & Web 端应用）</p>
          </div>
        </div>
        <div class="header-actions">
          <button class="action-btn" @click="handlePrint" title="打印或保存为PDF">
            <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none">
              <path d="M6 9V2h12v7M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2" />
              <path d="M6 14h12v8H6z" />
            </svg>
            打印 / 另存为 PDF
          </button>
        </div>
      </div>

      <!-- Tab 切换按钮：可直接在隐私政策与个人信息主体权利之间切换 -->
      <div class="tab-container">
        <button 
          class="tab-btn" 
          :class="{ active: currentTab === 'policy' }"
          @click="switchTab('policy')"
        >
          <span class="tab-icon">📄</span>
          隐私政策全文 (Privacy Policy)
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: currentTab === 'rights' }"
          @click="switchTab('rights')"
        >
          <span class="tab-icon">🛡️</span>
          个人信息主体权利与指引 (Privacy Rights)
        </button>
      </div>

      <div class="meta-strip">
        <span class="meta-item"><strong>版本编号：</strong>V1.0</span>
        <span class="meta-item"><strong>发布生效日期：</strong>2026 年 11 月 24 日</span>
        <span class="meta-item"><strong>最新更新日期：</strong>2026 年 11 月 24 日</span>
        <span class="meta-item"><strong>开发者/运营者：</strong>GouTou 研发团队</span>
      </div>
    </header>

    <div class="privacy-main">
      <!-- 快速导航侧边栏/锚点栏（桌面端悬浮） -->
      <aside class="toc-sidebar">
        <div class="toc-card">
          <h3 class="toc-title">目录导航</h3>
          <ul v-if="currentTab === 'policy'" class="toc-list">
            <li><a href="#summary">【特别重要提示】</a></li>
            <li><a href="#section-1">1. 我们如何收集和使用个人信息</a></li>
            <li><a href="#section-2">2. 设备权限调用与使用说明</a></li>
            <li><a href="#section-3">3. 第三方 SDK 及服务共享清单</a></li>
            <li><a href="#section-4">4. 个人信息的存储与安全保护</a></li>
            <li><a href="#section-5">5. 您的个人信息主体权利</a></li>
            <li><a href="#section-6">6. 未成年人隐私特别保护</a></li>
            <li><a href="#section-7">7. 隐私政策的变更与修订</a></li>
            <li><a href="#section-8">8. 联系我们与投诉反馈渠道</a></li>
          </ul>
          <ul v-else class="toc-list">
            <li><a href="#rights-overview">【权利保障概述】</a></li>
            <li><a href="#rights-access">1. 查阅与访问您的个人信息</a></li>
            <li><a href="#rights-modify">2. 更正与补充您的个人信息</a></li>
            <li><a href="#rights-delete">3. 删除您的个人信息</a></li>
            <li><a href="#rights-withdraw">4. 撤回同意与系统权限管理</a></li>
            <li><a href="#rights-cancel">5. 账号注销权与注销途径</a></li>
            <li><a href="#rights-copy">6. 复制与导出个人数据副本</a></li>
            <li><a href="#rights-complaint">7. 投诉与举报专职流程</a></li>
          </ul>
        </div>
      </aside>

      <!-- 正文内容区 -->
      <article class="privacy-content">
        <!-- ==================== TAB 1: 隐私政策全文 ==================== -->
        <section v-show="currentTab === 'policy'" class="doc-section">
          <!-- 核心提示框 -->
          <div id="summary" class="callout-box warning-box">
            <h4 class="callout-title">【重要提示与摘要】</h4>
            <p>
              感谢您使用 <strong>GouTou</strong>（以下简称“本应用”或“我们”）。我们深知个人信息对您的重要性，并始终严格遵守《中华人民共和国网络安全法》、《中华人民共和国个人信息保护法》(PIPL)、《常见类型移动互联网应用程序必要个人信息范围规定》及华为应用市场等应用分发平台的合规规范。
            </p>
            <p>
              <strong>特别提醒：</strong>
            </p>
            <ul>
              <li><strong>最小必要原则：</strong>在您仅浏览文章和公共资讯时，您无需注册或登录账号，我们不会收集您的身份标识信息。</li>
              <li><strong>权限调用前明确征得同意：</strong>本应用涉及的通知（`POST_NOTIFICATIONS`）及媒体存储权限（`READ_MEDIA_IMAGES` / `READ_EXTERNAL_STORAGE`），均在您主动触发对应业务功能时动态申请，绝不在后台静默获取，您可在系统设置中随时关闭或撤回授权。</li>
              <li><strong>第三方 SDK 清单明示：</strong>本应用接入了<strong>华为推送 SDK (Huawei Push Kit)</strong> 用于消息及提醒稳定触达，其收集的信息及隐私政策已在第三章详细披露。</li>
              <li><strong>账号注销渠道：</strong>我们提供便捷的账号注销途径，注销后我们将立即永久删除您的所有个人信息与数据。</li>
            </ul>
          </div>

          <h2 id="section-1" class="section-title">一、我们如何收集和使用您的个人信息</h2>
          <p>我们仅出于本政策所述的以下目的，遵循合法、正当、必要的原则收集和使用您的个人信息：</p>
          
          <div class="content-block">
            <h3>1.1 账号注册、登录与基本资料</h3>
            <p>
              当您注册并登录本应用账号时，我们需要收集您的 <strong>电子邮箱地址、设置的登录密码、用户昵称及个人头像</strong>。
            </p>
            <ul>
              <li><strong>电子邮箱：</strong>用于接收注册/登录验证码、重置密码凭证及保障账号安全唯一标识。</li>
              <li><strong>密码安全：</strong>您的密码将采用业界标准的不可逆加盐哈希（Salted Hash）算法进行单向加密后存储，任何人员（包括平台管理人员）均无法获知您的明文密码。</li>
              <li><strong>昵称与头像：</strong>用于在应用内展示您的个人身份形象。您可自主上传自定义头像图片。</li>
            </ul>
          </div>

          <div class="content-block">
            <h3>1.2 智能助理（GouTou Assistant / AI 对话）功能</h3>
            <p>
              当您使用智能助理功能时，我们会在经过您主动发送后，收集您输入的 <strong>对话文本内容、指令、问答记录</strong>。
            </p>
            <ul>
              <li>用于由大语言模型处理后向您返回回答，完成多轮对话、日程整理及日常资讯解答。</li>
              <li>历史会话记录仅关联您的登录账号并在云端加密保存，以便您在多端同步查阅历史记录。您可随时在界面上单向清空或删除指定的会话记录。</li>
            </ul>
          </div>

          <div class="content-block">
            <h3>1.3 定时提醒与日程任务（Cron 任务）</h3>
            <p>
              当您通过智能助理或定时设置配置提醒任务时，我们会收集您设置的 <strong>提醒事项标题、目标时间、提醒强度等级（时间衰减策略配置）</strong>。
            </p>
            <ul>
              <li>上述信息仅用于在您指定的时间段通过任务调度中心及华为推送通道，向您下发通知栏提醒；</li>
              <li>提醒强度的个性化设置存储于独立的扩展配置表中，与用户基本身份信息严格解耦。</li>
            </ul>
          </div>

          <div class="content-block">
            <h3>1.4 文章与社区发帖</h3>
            <p>
              当您在社区或博客分区发布文章、发帖或留言时，我们会收集您主动填写的 <strong>文章标题、分类、富文本正文、上传的插图与附件</strong>。
            </p>
            <ul>
              <li>上述内容将在应用内公开展示给其他用户浏览；</li>
              <li>您可以随时在“个人中心”或文章管理页面中对其进行编辑或删除。</li>
            </ul>
          </div>

          <div class="content-block">
            <h3>1.5 保障应用安全稳定运行与网络日志</h3>
            <p>
              为保障产品安全运行、预防恶意攻击及排查系统故障，在您使用本应用的过程中，我们的服务器会自动记录常规网络访问日志，包括：<strong>IP 地址、访问时间、请求接口、网络连接类型、系统错误诊断日志</strong>。此类信息不与您的身份信息进行关联，且在故障排查完毕后定期自动轮转覆写清理。
            </p>
          </div>

          <h2 id="section-2" class="section-title">二、设备权限调用与使用说明</h2>
          <p>
            为实现相应业务功能，本应用可能会向移动操作系统申请调用相关设备权限。我们承诺<strong>绝不会在未经您授权的情况下调用敏感权限，绝不在后台滥用权限，且您可随时在系统设置中自主关闭授权</strong>。
          </p>

          <div class="table-wrapper">
            <table class="info-table">
              <thead>
                <tr>
                  <th>权限名称</th>
                  <th>系统权限标识</th>
                  <th>使用场景与目的</th>
                  <th>是否可自主撤回</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>访问网络</strong></td>
                  <td><code>android.permission.INTERNET</code></td>
                  <td>用于应用与云端服务器进行安全数据传输，同步文章、进行 AI 智能问答及获取云端数据。</td>
                  <td>系统基础权限，应用运行所必需</td>
                </tr>
                <tr>
                  <td><strong>查看网络状态</strong></td>
                  <td><code>android.permission.ACCESS_NETWORK_STATE</code></td>
                  <td>用于检测当前是否连接 Wi-Fi 或移动数据网络，在无网络时给予友好提示，节省流量。</td>
                  <td>系统基础权限，应用运行所必需</td>
                </tr>
                <tr>
                  <td><strong>发送通知权限</strong></td>
                  <td><code>android.permission.POST_NOTIFICATIONS</code></td>
                  <td>用于在定时任务、日程提醒到达或系统关键业务消息时，向您手机通知栏弹出通知提醒。</td>
                  <td><strong>支持</strong>，可在系统设置中随时开启/关闭</td>
                </tr>
                <tr>
                  <td><strong>读取多媒体/相册</strong></td>
                  <td>
                    <code>android.permission.READ_MEDIA_IMAGES</code><br />
                    <code>android.permission.READ_EXTERNAL_STORAGE</code>
                  </td>
                  <td>仅在您主动更换个人头像或在发帖时上传本地图片时申请，用于在系统相册中选取图片。绝不读取未选中的其他私人照片。</td>
                  <td><strong>支持</strong>，仅在主动选择图片时触发授权</td>
                </tr>
                <tr>
                  <td><strong>外部存储写入</strong></td>
                  <td><code>android.permission.WRITE_EXTERNAL_STORAGE</code></td>
                  <td>仅在 Android 10 以下低版本系统中，用于本地缓存必要的离线文章与头像静态资源以提升流畅度。</td>
                  <td><strong>支持</strong>，可在系统设置中随时关闭</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h2 id="section-3" class="section-title">三、第三方 SDK 及服务共享清单</h2>
          <p>
            为确保 GouTou 部分核心功能（如在华为/鸿蒙设备上的定时提醒即时下发）稳定运行，我们接入了经严格安全评估的第三方 SDK 服务。我们将所有接入的第三方信息详尽披露如下：
          </p>

          <div class="table-wrapper">
            <table class="info-table">
              <thead>
                <tr>
                  <th>第三方服务名称</th>
                  <th>所属机构/提供方</th>
                  <th>使用目的与业务场景</th>
                  <th>收集的个人信息类型</th>
                  <th>官方隐私政策链接</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>华为推送 SDK (Huawei Push Kit / HMS Core)</strong></td>
                  <td>华为软件技术有限公司</td>
                  <td>为华为、荣耀及鸿蒙操作系统设备用户提供实时消息推送通道，保障日程提醒及时触达。</td>
                  <td>设备标识符（AAID、Push Token）、应用包名、系统版本、消息送达回执状态</td>
                  <td>
                    <a href="https://consumer.huawei.com/cn/privacy/privacy-policy/" target="_blank" rel="noopener noreferrer">
                      华为隐私声明 ↗
                    </a>
                  </td>
                </tr>
                <tr>
                  <td><strong>和风天气 API (QWeather)</strong></td>
                  <td>北京和风天气信息技术有限公司</td>
                  <td>在智能助理根据用户提问（如“查询今天珠海天气”）提供准确的天气预报信息。</td>
                  <td>用户主动询问的城市或地区名称（不收集 GPS 经纬度定位信息）</td>
                  <td>
                    <a href="https://www.qweather.com/terms/privacy.html" target="_blank" rel="noopener noreferrer">
                      和风天气隐私政策 ↗
                    </a>
                  </td>
                </tr>
                <tr>
                  <td><strong>阿里云对象存储 (Aliyun OSS)</strong></td>
                  <td>阿里云计算有限公司</td>
                  <td>用于持久化保存用户主动上传的公开文章插图、封面图片及用户个人头像图片。</td>
                  <td>用户主动上传的图片文件（不包含未经用户选择的文件）</td>
                  <td>
                    <a href="http://terms.aliyun.com/legal-agreement/terms/suit_bu1_ali_cloud/suit_bu1_ali_cloud201902141711_54837.html" target="_blank" rel="noopener noreferrer">
                      阿里云法律声明及隐私权政策 ↗
                    </a>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <h2 id="section-4" class="section-title">四、个人信息的存储与安全保护</h2>
          <div class="content-block">
            <h3>4.1 存储地点与存储期限</h3>
            <ul>
              <li><strong>存储地域：</strong>我们在中华人民共和国境内收集和产生的个人信息，将<strong>统一存储于中华人民共和国境内的合规云服务器（阿里云上海/杭州数据中心）</strong>，绝不会向境外转移或提供。</li>
              <li><strong>存储期限：</strong>我们仅在实现本隐私政策所述目的所需的最短必要期限内保留您的个人信息。在您主动申请注销账号后，我们将在 15 个工作日内核验身份并永久删除您的全部个人数据，或对个人信息进行不可恢复的匿名化脱敏处理。</li>
            </ul>
          </div>
          <div class="content-block">
            <h3>4.2 数据安全保障措施</h3>
            <ul>
              <li><strong>传输加密：</strong>客户端与服务端之间所有的网络请求均强制采用行业标准 <strong>HTTPS / TLS 1.2+</strong> 协议进行端到端加密传输，防止通信内容在传输过程中被窃听或篡改。</li>
              <li><strong>存储加密：</strong>用户密码使用高强度单向加盐散列算法存储；云数据库与敏感字段开启磁盘透明加密防护。</li>
              <li><strong>权限隔离：</strong>系统严格限制对数据库及内部微服务的直接访问，仅授权必要的技术人员通过双因素身份认证（2FA）并在操作审计监控下维护生产环境。</li>
            </ul>
          </div>

          <h2 id="section-5" class="section-title">五、您的个人信息主体权利</h2>
          <p>
            按照中华人民共和国《个人信息保护法》要求，您作为个人信息主体享有<strong>查阅、复制、更正、补充、删除个人信息以及撤回授权同意、注销账号</strong>等法定权利。
          </p>
          <p>
            为方便您快速行使权利，我们专门制作了详细的操作路径指引。您可以直接点击页面上方的 <strong>“个人信息主体权利与指引 (Privacy Rights)”</strong> 标签页查阅完整的行使流程。
          </p>

          <h2 id="section-6" class="section-title">六、未成年人隐私特别保护</h2>
          <p>
            我们非常重视对未成年人个人信息的保护：
          </p>
          <ul>
            <li>本应用主要面向具备完全民事行为能力的成年人。若您是未满 18 周岁的未成年人，请务必在您的父母或其他监护人的陪同与指导下阅读本政策，并在征得监护人明示同意后使用本产品及提供个人信息。</li>
            <li>对于经监护人同意而收集的未成年人个人信息，我们只会在法律允许、监护人明确同意或者保护未成年人所必要的情况下使用或公开披露。</li>
            <li>若您是未满 14 周岁的儿童，请勿自行注册或提交任何个人信息。如果我们发现在未事先获得可证实的监护人同意的情况下收集了未满 14 周岁儿童的个人信息，我们将第一时间设法尽快主动删除相关数据。</li>
          </ul>

          <h2 id="section-7" class="section-title">七、隐私政策的变更与修订</h2>
          <p>
            为给您提供更好的服务及随着法律法规的更新，我们可能会适时修订本隐私政策的内容：
          </p>
          <ul>
            <li>当本政策发生实质性变更时（例如收集目的、收集方式或个人信息处理范围发生重大变化），我们将在变更生效前通过应用内弹窗、系统通知或在官方网站显著位置向您提示并重新征得您的同意。</li>
            <li>您可以在本页面随时查看最新版本的隐私政策，页面顶部记录了最新生效及修订日期。</li>
          </ul>

          <h2 id="section-8" class="section-title">八、如何联系我们与投诉反馈</h2>
          <div class="contact-card">
            <p>如果您对本隐私政策或个人信息保护有任何疑问、意见、建议，或希望行使您的个人信息主体权利，您可以通过以下方式随时与我们取得联系：</p>
            <div class="contact-details">
              <div class="contact-row">
                <span class="contact-label">个人信息保护专职联系邮箱：</span>
                <a href="mailto:2460607806@qq.com" class="contact-value">2460607806@qq.com</a>
              </div>
              <div class="contact-row">
                <span class="contact-label">开发者/运营团队：</span>
                <span class="contact-value">GouTou 技术团队</span>
              </div>
              <div class="contact-row">
                <span class="contact-label">响应时效承诺：</span>
                <span class="contact-value highlight">我们将在核实验证您的用户身份后，在 <strong>15 个工作日内</strong> 给予答复和处理完毕。</span>
              </div>
            </div>
          </div>
        </section>

        <!-- ==================== TAB 2: 个人信息主体权利与指引 (隐私权利) ==================== -->
        <section v-show="currentTab === 'rights'" class="doc-section">
          <!-- 权利总览 -->
          <div id="rights-overview" class="callout-box success-box">
            <h4 class="callout-title">【个人信息主体权利法定保障承诺】</h4>
            <p>
              在 GouTou，我们尊重并全力保障您对个人信息的自主控制权。根据《中华人民共和国个人信息保护法》(PIPL) 第四章“个人在个人信息处理活动中的权利”及相关法律法规，您对您的个人信息享有充分的<strong>知情权、决定权、查阅权、复制权、更正权、删除权、撤回同意权以及账号注销权</strong>。
            </p>
            <p>
              本指引详细说明了您在 GouTou 应用中各项权利的具体行使路径与操作方式。
            </p>
          </div>

          <h2 id="rights-access" class="section-title">1. 查阅与访问您的个人信息</h2>
          <div class="content-block">
            <p>您有权访问我们在系统中保存的关于您的个人信息：</p>
            <div class="step-card">
              <div class="step-header">
                <span class="step-badge">操作路径</span>
                <h4>查阅账号与资料信息</h4>
              </div>
              <p>登录 GouTou 应用 -> 点击个人头像或侧边栏进入<strong>“个人中心 (Profile)”</strong>，即可查阅您的注册邮箱、用户昵称、个人头像以及历史发帖动态。</p>
            </div>
            <div class="step-card">
              <div class="step-header">
                <span class="step-badge">操作路径</span>
                <h4>查阅智能助理历史记录</h4>
              </div>
              <p>进入“创意应用中心” -> 打开<strong>“GouTou 助理”</strong>，在会话面板中可直接查阅与 AI 助手的全部历史对话问答记录及任务状态。</p>
            </div>
          </div>

          <h2 id="rights-modify" class="section-title">2. 更正与补充您的个人信息</h2>
          <div class="content-block">
            <p>当您发现我们处理的关于您的个人信息有错误、不准确或不完整时，您有权要求我们进行更正：</p>
            <div class="step-card">
              <div class="step-header">
                <span class="step-badge">操作路径</span>
                <h4>自主修改个人资料</h4>
              </div>
              <p>进入<strong>“个人中心 (Profile)”</strong> -> 点击头像区域可重新上传头像；在昵称输入框中可随时更新您的展示昵称，点击保存即刻生效。</p>
            </div>
            <p class="sub-text">如遇其他系统基础信息无法自行修改，您也可以发送邮件至 <a href="mailto:2460607806@qq.com">2460607806@qq.com</a>，我们将在核验身份后为您进行手动更正。</p>
          </div>

          <h2 id="rights-delete" class="section-title">3. 删除您的个人信息</h2>
          <div class="content-block">
            <p>在以下情形中，您可以向我们提出删除个人信息的请求：</p>
            <ul>
              <li>处理目的已实现、无法实现或者为实现处理目的不再必要；</li>
              <li>我们停止提供产品或者服务，或者保存期限已届满；</li>
              <li>您撤回了授权同意；</li>
              <li>我们违反法律、行政法规或者违反约定处理您的个人信息。</li>
            </ul>
            <div class="step-card">
              <div class="step-header">
                <span class="step-badge">操作路径</span>
                <h4>自主删除指定业务数据</h4>
              </div>
              <ul>
                <li><strong>删除已发布文章：</strong>在您的文章详情或个人中心，点击“删除”按钮即可将文章从云端彻底删除。</li>
                <li><strong>清空 AI 助理会话：</strong>在智能助手页面点击“清空上下文/新建会话”，即可清除历史会话记忆。</li>
              </ul>
            </div>
          </div>

          <h2 id="rights-withdraw" class="section-title">4. 撤回同意与系统权限管理</h2>
          <div class="content-block">
            <p>对于您授权给本应用调用的系统权限（如通知权限、媒体相册权限），您有权随时撤销授权：</p>
            <div class="step-card">
              <div class="step-header">
                <span class="step-badge">系统设置路径</span>
                <h4>撤回设备系统权限（Android & HarmonyOS 鸿蒙）</h4>
              </div>
              <ol>
                <li>打开手机系统<strong>“设置 (Settings)”</strong>；</li>
                <li>进入<strong>“应用与服务”</strong>或<strong>“应用管理”</strong>；</li>
                <li>在应用列表中找到并点击<strong>“GouTou”</strong>；</li>
                <li>点击<strong>“权限”</strong>，在权限列表中自主将“通知”或“存储/照片和视频”权限切换为“禁止”或“关闭”。</li>
              </ol>
            </div>
            <p class="sub-text">当您撤回同意或授权后，我们无法继续为您提供撤回同意所对应的特定功能（例如无法弹出定时通知），但这不会影响此前基于您的授权已开展的个人信息处理活动。</p>
          </div>

          <h2 id="rights-cancel" class="section-title">5. 账号注销权与注销指引（重要保障）</h2>
          <div class="content-block">
            <p>
              我们为您提供明确、便捷、不可撤销的<strong>账号注销服务</strong>。当您不再需要使用 GouTou 服务时，您可以选择注销账号：
            </p>
            
            <div class="callout-box warning-box">
              <h4 class="callout-title">【账号注销不可逆提示】</h4>
              <p>
                注销账号是不可恢复的操作。在注销完成后：
              </p>
              <ul>
                <li>您的账号将永久停止使用，无法再次以此凭证登录；</li>
                <li>您账号下所有的个人信息（包括昵称、邮箱、密码）、发布的全部文章、AI 历史对话数据、定时提醒配置及个人配置，均将<strong>在服务器端永久彻底删除或进行匿名化脱敏处理</strong>；</li>
                <li>上述数据一经删除将无法恢复，也无法再次找回。</li>
              </ul>
            </div>

            <div class="step-card">
              <div class="step-header">
                <span class="step-badge">方式一</span>
                <h4>通过个人中心在线提交注销申请</h4>
              </div>
              <p>登录账号 -> 进入<strong>“个人中心 (Profile)”</strong> -> 滚动至底部“账号安全”区域 -> 点击<strong>“注销账号”</strong>按钮并确认注销风险说明，验证通过后系统将进入注销清理流程。</p>
            </div>

            <div class="step-card">
              <div class="step-header">
                <span class="step-badge">方式二</span>
                <h4>发送邮件人工协助注销通道</h4>
              </div>
              <p>
                如您无法通过应用内界面操作，您可以通过您的注册邮箱向我们的官方个人信息保护邮箱发送注销申请：
              </p>
              <ul>
                <li><strong>接收邮箱：</strong><a href="mailto:2460607806@qq.com">2460607806@qq.com</a></li>
                <li><strong>邮件主题：</strong>申请注销 GouTou 账号 - [您的注册邮箱]</li>
                <li><strong>邮件正文：</strong>写明您的注册邮箱、用户昵称及注销意向说明。</li>
                <li><strong>处理时限承诺：</strong>我们将在收到邮件并核实验证您的账户归属身份后，在 <strong>15 个工作日内</strong> 彻底清除您的账号及全量关联个人数据并以邮件形式回复办理结果。</li>
              </ul>
            </div>
          </div>

          <h2 id="rights-copy" class="section-title">6. 复制与导出个人数据副本</h2>
          <div class="content-block">
            <p>
              您有权获取您提供给我们的基本个人信息副本。您可以通过发送邮件至 <a href="mailto:2460607806@qq.com">2460607806@qq.com</a> 说明导出诉求，我们将在完成身份安全核验后 15 个工作日内，以通用格式（如 JSON 或 CSV 电子文件）向您提供您的数据副本。
            </p>
          </div>

          <h2 id="rights-complaint" class="section-title">7. 投诉与举报专职流程</h2>
          <div class="content-block">
            <p>
              如您认为我们在个人信息处理活动中侵犯了您的合法权益，或者对我们的处理结果不满意，您可以通过以下方式投诉和反馈：
            </p>
            <div class="contact-card">
              <div class="contact-details">
                <div class="contact-row">
                  <span class="contact-label">投诉与举报专职邮箱：</span>
                  <a href="mailto:2460607806@qq.com" class="contact-value">2460607806@qq.com</a>
                </div>
                <div class="contact-row">
                  <span class="contact-label">处理时限：</span>
                  <span class="contact-value">自收到投诉之日起不超过 <strong>15 个工作日</strong></span>
                </div>
                <div class="contact-row">
                  <span class="contact-label">监管机构求助渠道：</span>
                  <span class="contact-value">您还可以依法向网信办、工业和信息化部（12321网络不良与垃圾信息举报受理中心）或市场监督管理部门投诉举报，或向有管辖权的人民法院提起诉讼。</span>
                </div>
              </div>
            </div>
          </div>
        </section>
      </article>
    </div>

    <!-- 底部简要版权 -->
    <footer class="privacy-footer">
      <div class="footer-inner">
        <p>© 2026 GouTou 研发团队. All Rights Reserved.</p>
        <p class="footer-note">本页面专用于 GouTou 应用隐私政策披露与个人信息主体权利行使，符合工信部及华为应用市场合规审核要求。</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

// 根据当前路由决定初始展示哪一个 Tab
const currentTab = ref('policy');

const syncTabFromRoute = () => {
  if (route.path.includes('rights')) {
    currentTab.value = 'rights';
    document.title = '个人信息主体权利与指引 - GouTou';
  } else {
    currentTab.value = 'policy';
    document.title = '隐私政策 - GouTou';
  }
};

onMounted(() => {
  syncTabFromRoute();
});

watch(() => route.path, () => {
  syncTabFromRoute();
});

const switchTab = (tab) => {
  currentTab.value = tab;
  if (tab === 'rights') {
    router.replace('/privacy-rights');
  } else {
    router.replace('/privacy-policy');
  }
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const handlePrint = () => {
  window.print();
};
</script>

<style scoped>
.privacy-container {
  width: 100%;
  min-height: 100vh;
  background-color: var(--bg-color, #ffffff);
  color: var(--text-color, #1a1a1a);
  display: flex;
  flex-direction: column;
}

/* 顶部 Header */
.privacy-header {
  background: var(--bg-color, #ffffff);
  border-bottom: 1px solid var(--border-color, rgba(0, 0, 0, 0.1));
  padding: 30px 40px 0 40px;
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.app-brand {
  display: flex;
  align-items: center;
  gap: 16px;
}

.app-logo {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #ff7e5f, #feb47b);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(254, 180, 123, 0.3);
}

.logo-emoji {
  font-size: 26px;
}

.brand-title {
  font-size: 22px;
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.3px;
}

.brand-subtitle {
  font-size: 13px;
  color: #666;
  margin-top: 4px;
}

.dark .brand-subtitle {
  color: #aaa;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid var(--border-color, #e0e0e0);
  background: transparent;
  color: var(--text-color, #333);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: rgba(0, 0, 0, 0.05);
}

.dark .action-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* Tabs 切换栏 */
.tab-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 12px;
  border-bottom: 2px solid transparent;
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  font-size: 15px;
  font-weight: 600;
  color: #666;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  transition: all 0.25s ease;
  margin-bottom: -1px;
}

.dark .tab-btn {
  color: #888;
}

.tab-btn:hover {
  color: var(--text-color, #000);
}

.tab-btn.active {
  color: #2563eb;
  border-bottom-color: #2563eb;
}

.dark .tab-btn.active {
  color: #60a5fa;
  border-bottom-color: #60a5fa;
}

.tab-icon {
  font-size: 16px;
}

/* 信息条 */
.meta-strip {
  max-width: 1200px;
  margin: 0 auto;
  padding: 10px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  font-size: 12px;
  color: #777;
  border-top: 1px dashed var(--border-color, rgba(0, 0, 0, 0.1));
}

.dark .meta-strip {
  color: #999;
}

/* 主体内容排版 */
.privacy-main {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 40px 20px;
  display: flex;
  gap: 40px;
  flex: 1;
}

/* 侧边目录 */
.toc-sidebar {
  width: 260px;
  flex-shrink: 0;
}

.toc-card {
  position: sticky;
  top: 180px;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid var(--border-color, rgba(0, 0, 0, 0.08));
  background: var(--bg-color, #ffffff);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
}

.toc-title {
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 12px;
  color: var(--text-color, #111);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.toc-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.toc-list li {
  margin-bottom: 8px;
}

.toc-list a {
  display: block;
  font-size: 13px;
  color: #555;
  text-decoration: none;
  line-height: 1.4;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.dark .toc-list a {
  color: #aaa;
}

.toc-list a:hover {
  color: #2563eb;
  background: rgba(37, 99, 235, 0.08);
}

.dark .toc-list a:hover {
  color: #60a5fa;
  background: rgba(96, 165, 250, 0.12);
}

/* 文章正文 */
.privacy-content {
  flex: 1;
  min-width: 0;
  line-height: 1.75;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  margin: 40px 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color, rgba(0, 0, 0, 0.1));
  color: var(--text-color, #111);
}

.section-title:first-of-type {
  margin-top: 0;
}

.content-block {
  margin-bottom: 24px;
}

.content-block h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 16px 0 8px 0;
  color: var(--text-color, #222);
}

p {
  margin-bottom: 12px;
  font-size: 14.5px;
  color: #333;
}

.dark p {
  color: #ccc;
}

ul, ol {
  margin: 8px 0 16px 24px;
  font-size: 14px;
  color: #444;
}

.dark ul, .dark ol {
  color: #bbb;
}

li {
  margin-bottom: 6px;
}

/* 提示卡片 */
.callout-box {
  padding: 18px 22px;
  border-radius: 10px;
  margin: 20px 0 28px 0;
  border-left: 4px solid;
}

.warning-box {
  background: rgba(245, 158, 11, 0.08);
  border-left-color: #f59e0b;
}

.success-box {
  background: rgba(16, 185, 129, 0.08);
  border-left-color: #10b981;
}

.callout-title {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 8px;
}

.warning-box .callout-title {
  color: #b45309;
}

.dark .warning-box .callout-title {
  color: #fbbf24;
}

.success-box .callout-title {
  color: #047857;
}

.dark .success-box .callout-title {
  color: #34d399;
}

/* 表格样式 */
.table-wrapper {
  overflow-x: auto;
  margin: 20px 0 28px 0;
  border: 1px solid var(--border-color, rgba(0, 0, 0, 0.1));
  border-radius: 10px;
}

.info-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13.5px;
  text-align: left;
}

.info-table th {
  background: rgba(0, 0, 0, 0.03);
  padding: 12px 16px;
  font-weight: 600;
  border-bottom: 1px solid var(--border-color, rgba(0, 0, 0, 0.1));
  color: var(--text-color, #111);
  white-space: nowrap;
}

.dark .info-table th {
  background: rgba(255, 255, 255, 0.05);
}

.info-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color, rgba(0, 0, 0, 0.06));
  color: #444;
}

.dark .info-table td {
  color: #bbb;
}

.info-table tr:last-child td {
  border-bottom: none;
}

.info-table code {
  background: rgba(0, 0, 0, 0.06);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-family: monospace;
}

.dark .info-table code {
  background: rgba(255, 255, 255, 0.1);
  color: #93c5fd;
}

.info-table a {
  color: #2563eb;
  text-decoration: none;
  font-weight: 500;
}

.dark .info-table a {
  color: #60a5fa;
}

.info-table a:hover {
  text-decoration: underline;
}

/* 操作指引卡片 */
.step-card {
  border: 1px solid var(--border-color, rgba(0, 0, 0, 0.08));
  border-radius: 10px;
  padding: 16px 20px;
  margin: 14px 0;
  background: rgba(0, 0, 0, 0.015);
}

.dark .step-card {
  background: rgba(255, 255, 255, 0.02);
}

.step-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.step-badge {
  background: #2563eb;
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
}

.step-card h4 {
  font-size: 14.5px;
  font-weight: 600;
  margin: 0;
}

.sub-text {
  font-size: 13px;
  color: #777;
  margin-top: 6px;
}

/* 联系方式卡片 */
.contact-card {
  border: 1px solid var(--border-color, rgba(0, 0, 0, 0.1));
  border-radius: 12px;
  padding: 24px;
  margin-top: 16px;
  background: rgba(37, 99, 235, 0.03);
}

.dark .contact-card {
  background: rgba(96, 165, 250, 0.04);
}

.contact-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 14px;
}

.contact-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 14px;
}

.contact-label {
  font-weight: 600;
  color: var(--text-color, #222);
}

.contact-value {
  color: #2563eb;
  text-decoration: none;
}

.dark .contact-value {
  color: #60a5fa;
}

.contact-value.highlight {
  color: #e11d48;
}

.dark .contact-value.highlight {
  color: #fb7185;
}

/* 底部 Footer */
.privacy-footer {
  border-top: 1px solid var(--border-color, rgba(0, 0, 0, 0.08));
  padding: 24px 20px;
  text-align: center;
  font-size: 12.5px;
  color: #888;
  background: var(--bg-color, #ffffff);
}

.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
}

.footer-note {
  margin-top: 4px;
  color: #999;
}

/* 响应式样式 */
@media (max-width: 900px) {
  .toc-sidebar {
    display: none;
  }

  .privacy-header {
    padding: 20px 20px 0 20px;
    position: relative;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .privacy-main {
    padding: 24px 16px;
  }

  .tab-btn {
    padding: 10px 14px;
    font-size: 14px;
  }
}

/* 打印样式支持 */
@media print {
  .privacy-header {
    position: static;
    border: none;
    padding: 0;
  }

  .toc-sidebar,
  .action-btn,
  .tab-container {
    display: none !important;
  }

  .privacy-main {
    padding: 0;
  }

  .privacy-content {
    width: 100%;
  }

  .table-wrapper {
    overflow: visible;
  }

  body {
    background: #fff !important;
    color: #000 !important;
  }
}
</style>
