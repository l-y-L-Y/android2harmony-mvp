/* Generated from Android ViewModel/Flow/LiveData state. */
import { ServiceRegistry } from '../common/ServiceRegistry';
import { MigratedRepository } from '../repositories/MigratedRepositories';

export class MigratedStore {
  isLoading: boolean = false;
  toastMessage: string | undefined = undefined;

  reset(): void {
    this.isLoading = false;
    this.toastMessage = undefined;
  }
}
