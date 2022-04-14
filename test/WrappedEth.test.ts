import { expect } from "chai";
import { BigNumber, ContractReceipt, ContractTransaction } from "ethers";
import { ethers } from "hardhat";

function getGasPrice(receipt: ContractReceipt): BigNumber {
  const gasUsed = receipt.gasUsed;
  const gasPrice = receipt.effectiveGasPrice;
  return gasUsed.mul(gasPrice);
}

async function getGasPriceFromTransaction(
  ctrans: ContractTransaction
): Promise<BigNumber> {
  const receipt = await ctrans.wait();
  return getGasPrice(receipt);
}

async function getDeployedLifeSuppportToken(): Promise<any> {
  const WrappedEthFactory = await ethers.getContractFactory("WrappedEth");
  const lifeSupportToken = await WrappedEthFactory.deploy(
    "Life Support",
    "LIFES"
  );
  await lifeSupportToken.deployed();
  return lifeSupportToken;
}

describe("WrappedEth", function () {
  it("Correct number of tokens are minted", async function () {
    const lifeSupportToken = await getDeployedLifeSuppportToken();
    const [owner] = await ethers.getSigners();

    await lifeSupportToken.deposit({
      value: ethers.utils.parseUnits("1.0", "wei"),
    });

    expect(await lifeSupportToken.balanceOf(owner.address)).to.equal(1000);
  });

  it("Deposit and withdraw works", async function () {
    const lifeSupportToken = await getDeployedLifeSuppportToken();
    const [owner] = await ethers.getSigners();
    const initialBalance = await lifeSupportToken.provider.getBalance(
      owner.address
    );

    // Deposit eth.
    const amountDespoitedWei = BigNumber.from("10");
    const amountTokenExpected = amountDespoitedWei.mul(1000);
    const depositTx = await lifeSupportToken.deposit({
      value: amountDespoitedWei,
    });
    const depositGasPrice = await getGasPriceFromTransaction(depositTx);
    const balanceAfterDeposit = await lifeSupportToken.provider.getBalance(
      owner.address
    );
    const amountWeiSpent = initialBalance.sub(balanceAfterDeposit);

    // Number of tokens is correct.
    expect(await lifeSupportToken.balanceOf(owner.address)).to.equal(
      amountTokenExpected
    );
    // Ether amount is correct.
    expect(amountWeiSpent).to.equal(amountDespoitedWei.add(depositGasPrice));
    expect(
      await lifeSupportToken.provider.getBalance(lifeSupportToken.address)
    ).to.equal(amountDespoitedWei);

    // Withdraw eth.
    const withdrawalGasPrice = await getGasPriceFromTransaction(
      await lifeSupportToken.withdraw(amountTokenExpected)
    );
    const balanceAfterWithdrawal = await lifeSupportToken.provider.getBalance(
      owner.address
    );
    const amountWeiReceived = balanceAfterWithdrawal.sub(balanceAfterDeposit);

    // Number of tokens is correct.
    expect(await lifeSupportToken.balanceOf(owner.address)).to.equal(
      BigNumber.from("0")
    );
    // Ether amount is correct.
    expect(amountWeiReceived).to.equal(
      amountDespoitedWei.sub(withdrawalGasPrice)
    );
    expect(
      await lifeSupportToken.provider.getBalance(lifeSupportToken.address)
    ).to.equal(BigNumber.from("0"));
  });

  it("Fails on withdrawal amount not multiple of 1000.", async function () {
    const lifeSupportToken = await getDeployedLifeSuppportToken();

    // Deposit eth.
    const amountDepositedWei = BigNumber.from("10");
    await lifeSupportToken.deposit({
      value: amountDepositedWei,
    });

    // Withdraw eth.
    await expect(lifeSupportToken.withdraw(10)).to.be.revertedWith(
      "Token withdrawal amount must be a multiple of 1000."
    );
    await expect(lifeSupportToken.withdraw(100)).to.be.revertedWith(
      "Token withdrawal amount must be a multiple of 1000."
    );
    await expect(lifeSupportToken.withdraw(999)).to.be.revertedWith(
      "Token withdrawal amount must be a multiple of 1000."
    );
    await expect(lifeSupportToken.withdraw(1001)).to.be.revertedWith(
      "Token withdrawal amount must be a multiple of 1000."
    );
    await expect(lifeSupportToken.withdraw(1999)).to.be.revertedWith(
      "Token withdrawal amount must be a multiple of 1000."
    );
  });

  it("Fails on withdrawal amount larger than deposit amount.", async function () {
    const lifeSupportToken = await getDeployedLifeSuppportToken();

    // Deposit eth.
    const amountDepositedWei = BigNumber.from("10");
    await lifeSupportToken.deposit({
      value: amountDepositedWei,
    });

    // Withdraw eth.
    await expect(lifeSupportToken.withdraw(11000)).to.be.revertedWith(
      "Can't withdraw more tokens than are in sender's account."
    );
  });

  it("Failure if you send eth directly to the contract.", async function () {
    const lifeSupportToken = await getDeployedLifeSuppportToken();
    const [owner] = await ethers.getSigners();

    // Deposit eth.
    await expect(
      owner.sendTransaction({
        to: lifeSupportToken.address,
        value: ethers.utils.parseEther("1.0"),
      })
    ).to.be.revertedWith("");
  });
});
