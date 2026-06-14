import { router } from '@kit.ArkUI'

@Entry @Component
export struct FragmentLogin {
  @State name: string = ''
  @State password: string = ''
  @State loadingVisible: boolean = false

  build() {
    Column() {
      // Back button
      Row() {
        Image($r('app.media.ic_previous_dark'))
          .width(24)
          .height(24)
          .objectFit(ImageFit.Contain)
          .onClick(() => {
            router.back()
          })
        Blank()
      }
      .width('100%')
      .height(24)
      .padding({ left: 16 })
      .margin({ top: 48 })

      // Title
      Text('欢迎来到 Jetpack MVVM 的世界')
        .fontSize(20)
        .fontColor('#000000')
        .textAlign(TextAlign.Center)
        .width('100%')
        .margin({ top: 120 })

      // Content
      Text('Welcome to the world of Jetpack MVVM best practice !')
        .fontSize(12)
        .fontColor('#000000')
        .textAlign(TextAlign.Center)
        .width('100%')
        .margin({ top: 8 })

      // Username input
      TextInput({ text: this.name, placeholder: '请输入用户名' })
        .type(InputType.Normal)
        .width('100%')
        .height(48)
        .margin({ left: 24, right: 24, top: 56 })
        .borderRadius(12)
        .border({ width: 1, color: '#FFEEEEEE' })
        .padding({ left: 12 })
        .onChange((value: string) => {
          this.name = value
        })

      // Password input
      TextInput({ text: this.password, placeholder: '请输入密码' })
        .type(InputType.Password)
        .width('100%')
        .height(48)
        .margin({ left: 24, right: 24, top: 24 })
        .borderRadius(12)
        .border({ width: 1, color: '#FFEEEEEE' })
        .padding({ left: 12 })
        .onChange((value: string) => {
          this.password = value
        })

      // Progress indicator
      if (this.loadingVisible) {
        LoadingProgress()
          .width(160)
          .height(36)
          .margin(24)
      }

      // Login button
      Button('登录')
        .width(200)
        .height(50)
        .backgroundColor('#FFFF7055')
        .borderRadius(25)
        .fontColor(Color.White)
        .fontSize(18)
        .fontWeight(FontWeight.Bold)
        .margin({ top: this.loadingVisible ? 24 : 72 })
        .onClick(() => {
          if (this.name === '' || this.password === '') {
            // TODO: show toast "用户名或密码不完整"
            return
          }
          // TODO: call AccountRequester.requestLogin(User(this.name, this.password))
          this.loadingVisible = true
        })
    }
    .width('100%')
    .height('100%')
    .backgroundColor(Color.White)
    .justifyContent(FlexAlign.Start)
    .alignItems(HorizontalAlign.Start)
  }
}