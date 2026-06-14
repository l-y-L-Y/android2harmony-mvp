import { router } from '@kit.ArkUI';

interface NotifyPlayerItem {
  id: number;
  songName: string;
  authorName: string;
}

@Entry
@Component
export struct NotifyPlayerSmall {
  @State isPlaying: boolean = true
  @State isLoading: boolean = false
  @State songName: string = "PureMusic"
  @State authorName: string = "未知艺术家"

  build() {
    Row() {
      // Album art (40x40, centerVertical, marginLeft 12)
      Image($r('app.media.bg_album_default'))
        .width(40)
        .height(40)
        .margin({ left: 12 })
        .objectFit(ImageFit.Fill)

      // Song name and author (vertical, marginLeft 64, marginRight 180)
      Column() {
        Text(this.songName)
          .fontSize(16)
          .fontColor('#ffffffff')
          .maxLines(1)
          .constraintSize({ maxWidth: 180 })

        Text(this.authorName)
          .fontSize(13)
          .fontColor('#ffffffff')
          .maxLines(1)
          .constraintSize({ maxWidth: 180 })
          .margin({ top: 2 })
      }
      .margin({ left: 52 })
      .alignItems(HorizontalAlign.Start)

      Blank()

      // Controls area: progress bar, prev, pause/play, next
      Row() {
        // Progress bar (loading indicator)
        LoadingProgress()
          .width(30)
          .height(30)
          .margin({ right: 16 })
          .color('#ffffffff')

        // Previous button (uses ic_next_dark as per original)
        Image($r('app.media.ic_next_dark'))
          .width(32)
          .height(32)
          .margin({ left: 8, right: 8 })
          .objectFit(ImageFit.Contain)
          .onClick(() => {
            // TODO: previous track
          })

        // Pause button (shown when playing)
        if (this.isPlaying) {
          Image($r('app.media.ic_action_pause'))
            .width(36)
            .height(36)
            .margin({ left: 8, right: 8 })
            .objectFit(ImageFit.Contain)
            .onClick(() => {
              this.isPlaying = false
            })
        }

        // Play button (shown when paused)
        if (!this.isPlaying) {
          Image($r('app.media.ic_action_play'))
            .width(36)
            .height(36)
            .margin({ left: 8, right: 8 })
            .objectFit(ImageFit.Contain)
            .onClick(() => {
              this.isPlaying = true
            })
        }

        // Next button (uses ic_previous_dark as per original)
        Image($r('app.media.ic_previous_dark'))
          .width(32)
          .height(32)
          .margin({ left: 8, right: 8 })
          .objectFit(ImageFit.Contain)
          .onClick(() => {
            // TODO: next track
          })
      }
      .height(48)
      .alignItems(VerticalAlign.Center)

      // Close button (alignParentEnd)
      Image($r('app.media.ic_close_white'))
        .width(40)
        .height(40)
        .padding(8)
        .objectFit(ImageFit.Contain)
        .margin({ right: 4 })
        .onClick(() => {
          router.back()
        })
    }
    .width('100%')
    .height(64)
    .backgroundColor('#fff0f0f0')
    .alignItems(VerticalAlign.Center)
  }
}