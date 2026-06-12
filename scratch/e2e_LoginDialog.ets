@Entry @Component
struct LoginDialog {
  @State isLoading: boolean = false
  @State account: string = ''
  @State password: string = ''
  @State rememberMe: boolean = true

  build() {
    Stack({ alignContent: Alignment.Center }) {
      // Main scrollable content
      Scroll() {
        Stack() {
          // Login form view
          if (!this.isLoading) {
            Column() {
              // Account input section
              Column() {
                Row() {
                  Text('账号')
                    .fontSize(16)
                    .fontWeight(FontWeight.Bold)
                    .fontColor('#ff000000')
                    .margin({ left: 8, top: 10 })
                  TextInput({ placeholder: '请输入账号', text: this.account })
                    .width('100%')
                    .height(40)
                    .fontSize(16)
                    .margin({ top: 10, left: 8, right: 8 })
                    .maxLines(1)
                    .inputType(InputType.Email)
                    .onChange((value: string) => { this.account = value })
                }

                Divider()
                  .margin({ top: 5, left: 2, right: 2 })

                Row() {
                  Text('密码')
                    .fontSize(16)
                    .fontWeight(FontWeight.Bold)
                    .fontColor('#ff000000')
                    .margin({ left: 8 })
                  TextInput({ placeholder: '请输入密码', text: this.password })
                    .width('100%')
                    .height(40)
                    .fontSize(16)
                    .margin({ left: 8, right: 8 })
                    .maxLines(1)
                    .type(InputType.Password)
                    .onChange((value: string) => { this.password = value })
                }
                .margin({ top: 7 })
              }
              .width('100%')
              .padding({ left: 15, right: 15, top: 30, bottom: 20 })
              .background('#f0f0f0')

              // Checkbox and login button section
              Column() {
                Row() {
                  Checkbox({ name: 'rememberMe', group: 'login' })
                    .select(this.rememberMe)
                    .onChange((value: boolean) => { this.rememberMe = value })
                    .margin({ left: 30 })
                  Text('记住我')
                    .fontSize(13)
                    .fontColor('#000000')
                    .margin({ left: 8 })
                }
                .margin({ top: 5 })
                .width('100%')

                Button('登录')
                  .width('100%')
                  .height(45)
                  .fontSize(20)
                  .margin({ top: 5 })
                  .onClick(() => {
                    // TODO: Handle login
                  })
              }
              .width('100%')
              .padding({ left: 15, right: 15 })
              .margin({ left: 15, right: 15 })
            }
            .width('100%')
            .height('100%')
            .alignItems(HorizontalAlign.Center)
          }

          // Loading view
          if (this.isLoading) {
            Column() {
              Progress()
                .width(135)
                .height(135)
            }
            .width(135)
            .height(135)
            .alignItems(HorizontalAlign.Center)
          }
        }
        .width('100%')
        .height('100%')
      }
      .width('100%')
      .height('100%')
      .scrollBar(BarState.Off)
      .align(Alignment.Center)
      .padding({ top: 14, left: 14, right: 14 })

      // Close button
      Button('')
        .width(40)
        .height(40)
        .position({ top: 14, right: 14 })
        .onClick(() => {
          // TODO: Handle close
        })
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#f0f0f0')
  }
}