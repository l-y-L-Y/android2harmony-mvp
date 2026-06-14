import router from '@ohos.router';

@Entry
@Component
export struct FragmentSearch {
  @State progress: number = 1
  @State progress_cancelable: number = 1
  @State enableDownload: boolean = true
  @State enableGlobalDownload: boolean = true
  @State globalDownloadInterval: number = 0
  @State lifecycleDownloadInterval: number = 0

  build() {
    Stack({ alignContent: Alignment.Center }) {
      Column() {
        Row() {
          Image($r('app.media.foreground'))
            .width(36)
            .height(36)
            .margin({ left: 12, top: 37 })
            .objectFit(ImageFit.Contain)
            .onClick(() => {
              router.back()
            })

          Column() {
            Text('《重学安卓》')
              .fontSize(18)
              .fontWeight(FontWeight.Bold)
              .margin({ left: 12, top: 37 })

            Text('付费读者加微信进群 myatejx')
              .fontSize(12)
              .fontColor('#999999')
              .margin({ left: 18, top: 4 })
          }

          Blank()

          Button('Learn More')
            .width(100)
            .height(32)
            .margin({ top: 37, right: 20 })
            .backgroundColor(0xffFF7055)
            .fontColor(Color.White)
            .fontSize(13)
            .fontWeight(FontWeight.Bold)
            .borderRadius(25)
            .onClick(() => {
              // TODO: Open external link
            })
        }
        .width('100%')

        Image($r('app.media.foreground'))
          .width(242)
          .height(242)
          .margin({ top: 24 })
          .objectFit(ImageFit.Contain)
          .onClick(() => {
            // TODO: Test navigation
          })

        Text('本页面用于测试 Navigation 路由导航')
          .fontSize(16)
          .visibility(Visibility.Hidden)

        Button('点击测试下载，返回页面仍有效')
          .height(32)
          .padding({ left: 12, right: 12 })
          .backgroundColor(this.enableGlobalDownload ? 0xffFF7055 : 0xffFFA07A)
          .fontColor(Color.White)
          .fontSize(13)
          .fontWeight(FontWeight.Bold)
          .enabled(this.enableGlobalDownload)
          .onClick(() => {
            if (!this.enableGlobalDownload) return
            this.enableGlobalDownload = false
            this.progress = 0
            this.globalDownloadInterval = setInterval(() => {
              this.progress++
              if (this.progress >= 20) {
                clearInterval(this.globalDownloadInterval)
                this.enableGlobalDownload = true
              }
            }, 500)
          })

        Button('点击测试下载，离开页面即中止')
          .height(32)
          .margin({ top: 12 })
          .padding({ left: 12, right: 12 })
          .backgroundColor(this.enableDownload ? 0xffFF7055 : 0xffFFA07A)
          .fontColor(Color.White)
          .fontSize(13)
          .fontWeight(FontWeight.Bold)
          .enabled(this.enableDownload)
          .onClick(() => {
            if (!this.enableDownload) return
            this.enableDownload = false
            this.progress_cancelable = 0
            this.lifecycleDownloadInterval = setInterval(() => {
              this.progress_cancelable++
              if (this.progress_cancelable >= 20) {
                clearInterval(this.lifecycleDownloadInterval)
                this.enableDownload = true
              }
            }, 500)
          })

        Progress({ value: this.progress, total: 20, type: ProgressType.Linear })
          .width('100%')
          .height(20)
          .margin({ left: 16, right: 16, top: 16 })
          .color(0xffFF7055)
          .backgroundColor('#E0E0E0')

        Progress({ value: this.progress_cancelable, total: 20, type: ProgressType.Linear })
          .width('100%')
          .height(20)
          .margin({ left: 16, right: 16, top: 16 })
          .color(0xffFF7055)
          .backgroundColor('#E0E0E0')
      }
      .width('100%')
      .height('100%')
      .backgroundColor(Color.White)
    }
    .width('100%')
    .height('100%')
  }

  aboutToDisappear() {
    clearInterval(this.globalDownloadInterval)
    clearInterval(this.lifecycleDownloadInterval)
  }
}