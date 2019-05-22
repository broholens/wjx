# wjx

问卷星问卷代刷



### NOTE
---
- 来源渠道：
  
  | 方式 | 示例                                                         |
  | ---- | ------------------------------------------------------------ |
  | 链接 | https://www.wjx.cn/jq/39410551.aspx                          |
  | 手机 | https://www.wjx.cn/m/39410551.aspx                           |
  | 微信 | https://www.wjx.cn/m/39410551.aspx?from=singlemessage&isappinstalled=0 |
  
- 参数starttime, rn, jqnonce均可在39410551.aspx中找到

- ktimes应该可以是个随机值(30~200)

- 参数jqsign在jqnew2.js中,下面为生成jqsign的函数,其中a参数是jqnonce
  ```javascript
  function dataenc(a) {
    var c, d, e, b = ktimes % 10;
    for (0 == b && (b = 1),
    c = [],
    d = 0; d < a.length; d++)
        e = a.charCodeAt(d) ^ b,
        c.push(String.fromCharCode(e));
    return c.join("")
  }
  ```

- 作答时间限制

- 验证码
